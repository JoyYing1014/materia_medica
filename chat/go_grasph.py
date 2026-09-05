from .answer_grasph import AnswerSearcher
from .question_analyze import QuestionPaser
from .question_classifier import QuestionClassifier
'''问答类'''
class ChatBotGraph:
    def __init__(self):
        self.classifier = QuestionClassifier()
        self.parser = QuestionPaser()

    def chat_main(self, sent):
        answer = '您好，有什么可以帮助您的吗'
        res_classify = self.classifier.classify(sent)
        if not res_classify:
            return answer
        # print(res_classify)
        res_sql = self.parser.parser_main(res_classify)
        # print(res_sql)
        #return res_sql
        final_answers = AnswerSearcher().search_main(res_sql)
        if not final_answers:
            return '您可以换个方式问问哦，如:某种药材的味道、别名、用法或您的症状等'
        else:
            return '\n'.join(final_answers)

if __name__ == '__main__':
    handler = ChatBotGraph()

    while 1:
        question = input('用户:')
        answer = handler.chat_main(question)
        print('Tom:', answer)
