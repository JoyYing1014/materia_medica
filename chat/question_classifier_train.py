from transformers import AdamW, get_linear_schedule_with_warmup, AutoTokenizer, AutoModel
import torch
from torch import nn
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')
import pandas as pd

# 加载数据
train_data = pd.read_csv('./chat/data/train.csv', encoding='utf-8')
PRE_TRAINED_MODEL_NAME = 'bert-base-chinese'
tokenizer = AutoTokenizer.from_pretrained(PRE_TRAINED_MODEL_NAME)

# 定义Dataset
class QuestionDataset(Dataset):
    def __init__(self, df, tokenizer, max_len):
        self.values = list(df['query'])
        self.labels = list(df['labelnum'])
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, item):
        label = self.labels[item]
        value = self.values[item]
        value_encoding = self.tokenizer.encode_plus(
            value,
            add_special_tokens=True,
            max_length=self.max_len,
            truncation=True,
            return_token_type_ids=False,
            pad_to_max_length=True,
            return_attention_mask=True,
            return_tensors='pt',
        )
        return {
            'question_input_ids': value_encoding['input_ids'].flatten(),
            'question_attention_mask': value_encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long),
        }

class SiameseBERTLSTM(nn.Module):
    def __init__(self, n_classes):
        super(SiameseBERTLSTM, self).__init__()
        self.bert = AutoModel.from_pretrained(PRE_TRAINED_MODEL_NAME)
        self.lstm = nn.LSTM(self.bert.config.hidden_size, self.bert.config.hidden_size, batch_first=True,
                            bidirectional=True)
        self.layer_norm = nn.LayerNorm(self.bert.config.hidden_size * 2)
        self.drop = nn.Dropout(p=0.3)
        self.fc1 = nn.Linear(self.bert.config.hidden_size * 2, 2048)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(2048, n_classes)

    def forward(self, input_ids, attention_mask):
        bert_output = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask,
            return_dict=False
        )
        lstm_output, _ = self.lstm(bert_output[0])
        lstm_output = self.layer_norm(lstm_output)
        pooled_output = torch.mean(lstm_output, 1)
        output = self.drop(pooled_output)
        output = self.fc1(output)
        output = self.relu(output)
        return self.fc2(output)

def create_data_loader(df, tokenizer, max_len, batch_size):
    ds = QuestionDataset(
        df=df,
        tokenizer=tokenizer,
        max_len=max_len
    )
    return DataLoader(
        ds,
        batch_size=batch_size,
        shuffle=True
    )


df_train, df_val = train_test_split(train_data, test_size=0.2,random_state=42)
train_data_loader = create_data_loader(df_train, tokenizer, 40, 4)
val_data_loader = create_data_loader(df_val, tokenizer,40,4 )

# 训练模型
device = 'mps'
model = SiameseBERTLSTM(len(train_data['labelnum'].unique()))
model = model.to(device)


EPOCHS = 10
optimizer = AdamW(model.parameters(), lr=2e-5, correct_bias=False)

total_steps = len(train_data_loader) * EPOCHS
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=0,
    num_training_steps=total_steps
)
loss_fn = nn.CrossEntropyLoss()


def train_epoch(model, data_loader, loss_fn, optimizer, device, scheduler):
    model = model.train()
    accu_loss = torch.zeros(1).to(device)
    accu_num = torch.zeros(1).to(device)
    sample_num = 0
    data_loader = tqdm(data_loader)
    for step, data in enumerate(data_loader):
        input_ids = data["question_input_ids"].to(device)
        attention_mask = data["question_attention_mask"].to(device)
        targets = data["labels"].to(device)
        sample_num += input_ids.shape[0]
        outputs = model(input_ids, attention_mask)
        loss = loss_fn(outputs, targets)
        loss.backward()
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()

        accu_loss += loss.item()
        preds = torch.argmax(outputs, dim=1)
        accu_num += (preds == targets).sum().item()
        data_loader.desc = "[train epoch {}] loss: {:.3f}, acc: {:.3f}".format(
            epoch, accu_loss.item() / (step + 1), accu_num.item() / sample_num
        )
    return accu_loss.item() / (step + 1), accu_num.item() / sample_num

def eval_model(model, data_loader, loss_fn, device):
    model = model.eval()
    accu_loss = torch.zeros(1).to(device)
    accu_num = torch.zeros(1).to(device)
    sample_num = 0
    data_loader = tqdm(data_loader)
    with torch.no_grad():
        for step, data in enumerate(data_loader):
            input_ids = data["question_input_ids"].to(device)
            attention_mask = data["question_attention_mask"].to(device)
            targets = data["labels"].to(device)
            outputs = model(input_ids, attention_mask)
            loss = loss_fn(outputs, targets)

            accu_loss += loss.item()
            preds = torch.argmax(outputs, dim=1)
            accu_num += (preds == targets).sum().item()
            sample_num += input_ids.shape[0]
            data_loader.desc = "[valid epoch {}] loss: {:.3f}, acc: {:.3f}".format(
                epoch, accu_loss.item() / (step + 1), accu_num.item() / sample_num
            )

    return accu_loss.item() / (step + 1), accu_num.item() / sample_num


history = defaultdict(list)
best_loss = float('inf')
best_acc = 0

for epoch in range(EPOCHS):
    train_loss, train_acc = train_epoch(model, train_data_loader, loss_fn, optimizer, device, scheduler)
    val_loss, val_acc = eval_model(model, val_data_loader, loss_fn, device)

    history['train_loss'].append(train_loss)
    history['train_acc'].append(train_acc)
    history['val_loss'].append(val_loss)
    history['val_acc'].append(val_acc)

    if train_acc> best_acc:
        torch.save(model.state_dict(), './chat/good.bin')
        best_acc = train_acc