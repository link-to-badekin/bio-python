"""
Написать программу, которая для заданного автора находит
статьи в Pubmed, создает массив из их ключевых слов, находит
статьи за последний год с использованием одного из этих
ключевых слов и возвращает гены, связанные с этими статьями.
"""



#модули
#для обработки ошибок с сетью
import time


from Bio import Entrez
from Bio import Medline

#Настройка переменных модуля
Entrez.email = ''
#retmax - максимальное количество возвращаемых записей, по умолчанию 20 
# field - поиск по конкретному полю:
#reldate 
""" 
	When reldate is set to an integer n, the search returns only those 
	items that have a date specified by datetype within the last n days.
"""
def get_id_articles(author):
	"""Получаем id не более retmax статей автора"""
	while True: 
		try:
			#поисковой запрос 
			handle = Entrez.esearch(db="pubmed", term=author+"[AUTHOR]",retmax = 5 ) 
			records = Entrez.read(handle)
			handle.close()
			break;
		except IOError :
			print("Ошибка сети \n")
			print("повторное соединение через 15 секунд\n")
			time.sleep(15)
			#отдыхаем 15 секунд и верим в чудо от провайдера 
	#Забираем id-шники из словаря  
	return records["IdList"]

def get_keywords_articles (id_list):
	"""Забираем ключевые слова из статей, если они есть """
	keywords = []
	while True: 
		try:
			#Получаем список статей по id с сервера 
			handle = Entrez.efetch(db="pubmed", id=id_list, retmode="text", rettype="medLine")
			#Приводим в адекватный вид 
			records = Medline.parse(handle)
			break;
		except IOError :
			print("Ошибка сети \n")
			print("повторное соединение через 15 секунд\n")
			time.sleep(15)
	
	#получили записи в виде итерационного объекта
	for record in records:
		#проверка есть ли ключевые слова или можем получить ошибку исполнения
		#'OT' - раздел Other Term 
		if 'OT' in record:
			for word in record['OT']:
				#проверка на дублирующиеся ключевые слова 
				if word not in keywords:
					keywords.append(word)
	handle.close()
	return keywords

def get_articles_by_keywords (keywords):
	"""Получаем статьи по ключевым словам за последние 365 дней, по каждому слову не более retmax"""
	#проверка на уникальность с помощью множеств, можно заменить in
	id_list = set()
	try:
		for keyword in keywords:
			#pdat - по дате публикации 
			handle = Entrez.esearch(db="pubmed", term =keyword, datetype = 'pdat' ,reldate = 365, retmax = 20)
			records = Entrez.read(handle)
			id_set = set(records['IdList'])
			#складываем уникальные элементы 
			id_list |= id_set
			handle.close()
	except IOError :
			print("Ошибка сети \n")
	#делаем из множества список и отправляем дальше
	return list(id_list)

def get_gene_id(id_list):
	gene_list = []
	while True: 
		try:
			#dbfrom откуда, где проверяем linkname, что id, можно список или один id
			handle = Entrez.elink(dbfrom="pubmed", linkname='pubmed_gene', id=id_list)
			records = Entrez.read(handle)
			break
		except IOError :
			print("Ошибка сети \n")
			print("повторное соединение через 15 секунд\n")
			time.sleep(15)
	for record in records:
		if record['LinkSetDb']:
			#[{'Link': [{'Id': '3887'}], 'DbTo': 'gene', 'LinkName': 'pubmed_gene'}]
			ids = record['LinkSetDb'][0]['Link']
			for item in  ids :
				for id in item:
					if item[id] not in gene_list:
						gene_list.append(item[id])
	handle.close()
	return gene_list

author = input('Введите автора статьи:')
#получаем статьи автора
id_list = get_id_articles(author)
#Ключивые слова 
keywords = get_keywords_articles(id_list)
#поиск статей по ключивым словам за год 
id_list = get_articles_by_keywords(keywords)
print('Я еще работаю \n')
#id генов
gene_list = get_gene_id(id_list)
print(len(keywords))
print(len(id_list))
print (len(gene_list))
