from py2neo import Graph
from py2neo import Node, Relationship


def read_data(file_path):
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            data.append(line.strip())
    return data


# 读取中药数据
names = read_data('./chat/data/name.txt')
aliases = read_data('./chat/data/alias.txt')
smells = read_data('./chat/data/smell.txt')
cures = read_data('./chat/data/cure.txt')
parts = read_data('./chat/data/part.txt')
symptoms = read_data('./chat/data/symptom.txt')
causes = read_data('./chat/data/cause.txt')
therapy = read_data('./chat/data/therapy.txt')

graph = Graph('bolt://localhost:7687', auth=('neo4j', 's'))
graph.delete_all()

for name, alias, smell, cure in zip(names, aliases, smells, cures):
    # 创建中药节点
    med_node = Node('中药', name=name)
    graph.merge(med_node, '中药', 'name')

    # 创建别名节点并建立关系
    alias_node = Node('别名', name=alias)

    # 创建气味品质节点并建立关系
    smell_node = Node('气味品质', name=smell)

    # 创建主治方法节点并建立关系
    cure_node = Node('主治方法', name=cure)

    relat_one = Relationship(med_node, '别名是', alias_node)
    relat_two = Relationship(med_node, '气味品质是', smell_node)
    relat_three = Relationship(med_node, '使用方法是', cure_node)

    graph.create(relat_one)
    graph.create(relat_two)
    graph.create(relat_three)

for symptom, cause, therapy in zip(symptoms, causes, therapy):
    # 创建症状节点
    med_node = Node('症状', name=symptom)
    graph.merge(med_node, '症状', 'name')

    # 创建病因节点并建立关系
    cause_node = Node('病因', name=cause)

    # 创建疗法节点并建立关系
    therapy_node = Node('疗法', name=therapy)

    relate_one = Relationship(med_node, '病因是', cause_node)
    relate_two = Relationship(med_node, '疗法是', therapy_node)

    graph.create(relate_one)
    graph.create(relate_two)
