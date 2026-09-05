from py2neo import Graph
from django.conf import settings


class KnowledgeGraphUnavailable(RuntimeError):
    """Raised when the configured Neo4j knowledge graph cannot serve a request."""

class AnswerSearcher:
    def __init__(self):
        try:
            self.g = Graph(
                settings.NEO4J_URI,
                auth=(settings.NEO4J_USERNAME, settings.NEO4J_PASSWORD),
                name=settings.NEO4J_DATABASE,
            )
        except Exception as exc:
            raise KnowledgeGraphUnavailable(
                '知识图谱服务不可用，请检查 Neo4j 连接配置和服务状态。'
            ) from exc
        self.num_limit = 20

    '''执行cypher查询，并返回相应结果'''

    def search_main(self, sqls):
        final_answers = []
        for sql_ in sqls:
            question_type = sql_['question_type']
            queries = sql_['sql']
            answers = []
            for query in queries:
                try:
                    ress = self.g.run(query).data()
                except Exception as exc:
                    raise KnowledgeGraphUnavailable(
                        '知识图谱服务不可用，请检查 Neo4j 连接配置和服务状态。'
                    ) from exc
                answers += ress
            # name_part
            # [{'b.name': '水部'}]
            final_answer = self.answer_prettify(question_type, answers)
            if final_answer:
                final_answers.append(final_answer)
        return final_answers

    '''根据对应的qustion_type，调用相应的回复模板'''
    def answer_prettify(self, question_type, answers):
        final_answer = []
        if not answers:
            return ''
        if question_type == 'name_part':
            desc = [i['b.name'] for i in answers]#KeyError: 'n.name'
            #print(''.join(list(set(desc))))
            final_answer = (''.join(list(set(desc))))
            #print(final_answer)
        elif question_type == 'name_alias':
            desc = [i['b.name'] for i in answers]
            final_answer = ( ''.join(list(set(desc))))
        elif question_type == 'name_smell':
            desc = [i['b.name'] for i in answers]
            final_answer = ( ''.join(list(set(desc))))
        elif question_type == 'name_cure':
            desc = [i['b.name'] for i in answers]
            final_answer = (''.join(list(set(desc))))
        elif question_type == 'symptom_cause':
            desc = [i['b.name'] for i in answers]
            final_answer = (''.join(list(set(desc))))
        elif question_type == 'symptom_therapy':
            desc = [i['b.name'] for i in answers]
            final_answer = (''.join(list(set(desc))))
        return final_answer
if __name__ == '__main__':
    searcher = AnswerSearcher()
    #searcher.search_main([{'question_type': 'name_part', 'sql': ["MATCH (n)-[r:属于]-(b) where n:中药 and n.name='腊雪' return b.name"]}])
