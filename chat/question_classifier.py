from functools import lru_cache

import ahocorasick
import pandas as pd
import torch
from django.conf import settings
from torch import nn
from transformers import AutoModel, AutoTokenizer


class ChatModelUnavailable(RuntimeError):
    """Raised when the locally configured question-classification model is unavailable."""

class Classify(nn.Module):
    def __init__(self, encoder, n_classes):
        super(Classify, self).__init__()
        self.bert = encoder
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

def _get_device():
    requested = settings.CHAT_MODEL_DEVICE.strip().lower()
    if requested == 'cpu':
        return torch.device('cpu')
    if requested == 'cuda' and torch.cuda.is_available():
        return torch.device('cuda')
    if requested == 'mps' and getattr(torch.backends, 'mps', None) and torch.backends.mps.is_available():
        return torch.device('mps')
    raise ChatModelUnavailable(
        'CHAT_MODEL_DEVICE 配置不可用。Windows 本地运行请使用 cpu，'
        '或在具备对应硬件和驱动的服务器上使用 cuda。'
    )


@lru_cache(maxsize=1)
def get_inference_components():
    """Load the tokenizer and trained classifier only when chat is requested."""
    model_dir = settings.CHAT_MODEL_DIR
    weights_path = settings.CHAT_MODEL_WEIGHTS
    if not model_dir.is_dir():
        raise ChatModelUnavailable(
            '聊天基础模型未配置。请将完整的 bert-base-chinese 模型放到 '
            'CHAT_MODEL_DIR 指定的目录。'
        )
    if not weights_path.is_file():
        raise ChatModelUnavailable('找不到聊天分类器权重文件，请检查 CHAT_MODEL_WEIGHTS。')

    try:
        tokenizer = AutoTokenizer.from_pretrained(
            str(model_dir), local_files_only=settings.CHAT_MODEL_LOCAL_FILES_ONLY
        )
        encoder = AutoModel.from_pretrained(
            str(model_dir), local_files_only=settings.CHAT_MODEL_LOCAL_FILES_ONLY
        )
        device = _get_device()
        model = Classify(encoder, n_classes=5).to(device)
        state_dict = torch.load(weights_path, map_location=device, weights_only=True)
        model.load_state_dict(state_dict)
        model.eval()
    except (OSError, RuntimeError, ValueError) as exc:
        raise ChatModelUnavailable('聊天模型加载失败，请检查本地模型、权重和设备配置。') from exc
    return tokenizer, model, device


def make_encoding(text, tokenizer):
    return tokenizer.encode_plus(
        text,
        add_special_tokens=True,
        max_length=40,
        truncation=True,
        return_token_type_ids=False,
        padding='max_length',
        return_attention_mask=True,
        return_tensors='pt',
    )


@lru_cache(maxsize=1)
def get_labels():
    train_data = pd.read_csv(settings.CHAT_DATA_DIR / 'train.csv', encoding='utf-8')
    labels = tuple(train_data['label'].dropna().unique())
    if len(labels) != 5:
        raise ChatModelUnavailable('训练标签文件异常，无法确定聊天分类类别。')
    return labels


def predict(encoding, labels, model, device):
    with torch.inference_mode():
        outputs = model(
            input_ids=encoding['input_ids'].to(device),
            attention_mask=encoding['attention_mask'].to(device),
        )
        prediction = torch.argmax(outputs, dim=1).item()
    return labels[prediction]


class QuestionClassifier:
    def __init__(self):
        data_dir = settings.CHAT_DATA_DIR
        self.part_path = data_dir / 'part.txt'
        self.name_path = data_dir / 'name.txt'
        self.alias_path = data_dir / 'alias.txt'
        self.smell_path = data_dir / 'smell.txt'
        self.cure_path = data_dir / 'cure.txt'
        self.symptom_path = data_dir / 'symptom.txt'
        self.cause_path = data_dir / 'cause.txt'
        self.therapy_path = data_dir / 'therapy.txt'
        #加载特征词
        self.part_wds=[i.strip() for i in open(self.part_path,encoding="utf-8") if i.strip()]
        self.name_wds = [i.strip() for i in open(self.name_path, encoding="utf-8") if i.strip()]
        self.alias_wds = [i.strip() for i in open(self.alias_path, encoding="utf-8") if i.strip()]
        self.smell_wds = [i.strip() for i in open(self.smell_path, encoding="utf-8") if i.strip()]
        self.cure_wds = [i.strip() for i in open(self.cure_path, encoding="utf-8") if i.strip()]
        self.symptom_wds = [i.strip() for i in open(self.symptom_path, encoding="utf-8") if i.strip()]
        self.cause_wds = [i.strip() for i in open(self.cause_path, encoding="utf-8") if i.strip()]
        self.therapy_wds = [i.strip() for i in open(self.therapy_path, encoding="utf-8") if i.strip()]
        # 创建了包含5类实体特征词的元素集
        self.region_words = set(self.part_wds + self.name_wds + self.alias_wds+ self.smell_wds+ self.cure_wds+self.symptom_wds + self.cause_wds + self.therapy_wds)
        # 构造领域actree
        self.region_tree = self.build_actree(list(self.region_words))
        # 构建词典
        self.wdtype_dict = self.build_wdtype_dict()

    def build_wdtype_dict(self):
        # 该函数是检查问句中涉及的5类实体，并返回一个列表
        wd_dict = dict()
        for wd in self.region_words:
            wd_dict[wd] = []
            if wd in self.part_wds:
                wd_dict[wd].append('part')
            if wd in self.name_wds:
                wd_dict[wd].append('name')
            if wd in self.alias_wds:
                wd_dict[wd].append('alias')
            if wd in self.smell_wds:
                wd_dict[wd].append('smell')
            if wd in self.cure_wds:
                wd_dict[wd].append('cure')
            if wd in self.symptom_wds:
                # print('101')
                wd_dict[wd].append('symptom')
            if wd in self.therapy_wds:
                wd_dict[wd].append('therapy')
            if wd in self.cause_wds:
                wd_dict[wd].append('cause')
        return wd_dict

    '''基于特征词进行分类'''

    def check_words(self, wds, sent):
        for wd in wds:
            if wd in sent:
                return True
        return False
#检查是否有实体类型的特征词
    '''构造actree，加速过滤'''

    def build_actree(self, wordlist):
        # 往actree中添加数据，这是已经封装好的模块
        actree = ahocorasick.Automaton()
        for index, word in enumerate(wordlist):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    '''构造词对应的类型'''
    def check_medical(self, question):
        #该模块是通过匹配找到问句中存在的5类实体
        region_wds = []
        #iter()是迭代器对象从集合的第一个元素开始访问，直到所有的元素被访问完结束。迭代器只能往前不会后退
        for i in self.region_tree.iter(question):#对问句进行多匹配模式的迭代
            wd = i[1][1]
            region_wds.append(wd)
        stop_wds = []
        for wd1 in region_wds:
            for wd2 in region_wds:
                if wd1 in wd2 and wd1 != wd2:
                    stop_wds.append(wd1)
        final_wds = [i for i in region_wds if i not in stop_wds]
        final_dict = {i : self.wdtype_dict.get(i) for i in final_wds}

        return final_dict
    '''分类主函数'''

    def classify(self, question):
        data = {}
        medical_dict = self.check_medical(question)  # 问句过滤
        if not medical_dict:
            return {}
        data['args'] = medical_dict
        tokenizer, model, device = get_inference_components()
        encoding = make_encoding(question, tokenizer)
        data['question_types'] = [predict(encoding, get_labels(), model, device)]
        return data


if __name__ == '__main__':
    handler = QuestionClassifier()
    while 1:
        question = input('输入您的问题:')
        data = handler.classify(question)
        print(data)
        #{'args': {'腊雪': ['name']}, 'question_types': ['name_part']}
