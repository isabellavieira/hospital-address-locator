# -*- coding: utf-8 -*-

#---------------------------------------------------------------------------------#
# By Isabella Vieira Ferreira													  #
# Script to get a hospital address using Google Places API based on a excel sheet #
# that contains a list of hospitals												  #
#---------------------------------------------------------------------------------#

import requests
from xml.etree import ElementTree
import pandas as pd
import numpy as np
from firebase import firebase as fb
import json
import csv
import os

#--------------------------------------------------------------------------------#
#																				 #
#--------------------------------------------------------------------------------#
def saveFirebase(firebase, jsonData):

	result = firebase.post("/HospitaisBrasil", jsonData)

#--------------------------------------------------------------------------------#
#																				 #
#--------------------------------------------------------------------------------#
def saveCSV(arquivo_csv, jsonData):

	nome = jsonData["nome"].encode('utf-8')
	tipo = jsonData["tipo"].encode('utf-8')
	endereco = jsonData["localizacao"]["endereco"].encode('utf-8')
	cidade = jsonData["localizacao"]["cidade"].encode('utf-8')
	estado = jsonData["localizacao"]["estado"].encode('utf-8')
	latitude = jsonData["localizacao"]["lat"]
	longitude = jsonData["localizacao"]["lng"]
	
	#print ">>>>> SAVE CSV"
	#print "nome: ", nome
	#print "tipo: ", tipo
	#print "lat: ", latitude
	#print "long: ", longitude
	#print "endereco: ", endereco

	arquivo_csv.writerow([nome, tipo, endereco, cidade, estado, latitude, longitude])

#--------------------------------------------------------------------------------#
#																				 #
#--------------------------------------------------------------------------------#
def saveSQL(arquivo_sql, jsonData):

	nome = jsonData["nome"].encode('utf-8').strip(" ")
	tipo = jsonData["tipo"].encode('utf-8')
	endereco = jsonData["localizacao"]["endereco"].encode('utf-8')
	cidade = jsonData["localizacao"]["cidade"].encode('utf-8')
	estado = jsonData["localizacao"]["estado"].encode('utf-8')
	latitude = jsonData["localizacao"]["lat"]
	longitude = jsonData["localizacao"]["lng"]

	sql = """INSERT INTO Hospitais (nome, tipo, endereco, cidade, estado, latitude, longitude) VALUES ('%s', '%s', '%s', '%s', '%s', %f, %f);"""
	query = (sql % (nome, tipo, endereco, cidade, estado, latitude, longitude))

	#print "SQL: ", query
	arquivo_sql.write(query)
	arquivo_sql.write('\n')

#--------------------------------------------------------------------------------#
#																				 #
#--------------------------------------------------------------------------------#
def requestAdress (hospitals, firebase, tipoHospital, indexFrom):

	API_KEY = ["AIzaSyD0I7JeXCF044fHzhyLsxCrMUVoJdvb3cM", "AIzaSyB6Pjw3Bh0juZNsOCZ_OPiZ_ECQhzTiMQU", "AIzaSyCPVDwcx1bQB10fH_GqnXiEe0M7PSrl9pk", "AIzaSyB6NFAcgnUA3o-ErQ39eYrrft8-v-9lASA","AIzaSyBWGUFtgh31UQd2fU-DrGQ-ydqKb5mEHXg", "AIzaSyAb7AJfGi64tjj7l31qyAAV4OC-Tuuhs4c"]

	limiteRequisicoes = 0
	chave_API_KEY = 0
	naoSalvou = []
	sent = []
	"""arquivo_overquerylimit = open("over_query_limit.txt", "a")
	arquivo_naoSalvouBD = open("naoSalvouBD.txt", "a")
	arquivo_csv = csv.writer(open("dadosHospitais.csv", "a"))
	arquivo_sql = open("dadosHospitais.sql", "a")"""

	arquivo_overquerylimit = open("over_query_limit_especializado.txt", "a")
	arquivo_naoSalvouBD = open("naoSalvouBD_especializado.txt", "a")
	arquivo_csv = csv.writer(open("dadosHospitais.csv", "a"))
	arquivo_sql = open("dadosHospitais.sql", "a")

	#os.chmod("/Users/isabellavieira/Desktop/Crawler Hospitais iMergency/dadosHospitais.csv", 777)
	#os.chmod("/Users/isabellavieira/Desktop/Crawler Hospitais iMergency/dadosHospitais.sql", 777)
	#os.chmod("/Users/isabellavieira/Desktop/Crawler Hospitais iMergency/naoSalvouBD.txt", 777)
	#os.chmod("/Users/isabellavieira/Desktop/Crawler Hospitais iMergency/over_query_limit.txt", 777)

	#arquivo_csv.writerow(["nome", "tipo", "endereco", "cidade", "estado", "latitude", "longitude"])

	arquivo_overquerylimit.close()
	arquivo_naoSalvouBD.close()
	#arquivo_csv.close()
	arquivo_sql.close()


	i = indexFrom
	while (i < len(hospitals)):

		"""arquivo_overquerylimit = open("over_query_limit.txt", "a")
		arquivo_naoSalvouBD = open("naoSalvouBD.txt", "a")
		arquivo_csv = csv.writer(open("dadosHospitais.csv", "a"))
		arquivo_sql = open("dadosHospitais.sql", "a")"""

		arquivo_overquerylimit = open("over_query_limit_especializado.txt", "a")
		arquivo_naoSalvouBD = open("naoSalvouBD_especializado.txt", "a")
		arquivo_csv = csv.writer(open("dadosHospitais.csv", "a"))
		arquivo_sql = open("dadosHospitais.sql", "a")

		#arquivo_csv.writerow(["nome", "tipo", "endereco", "latitude", "longitude"])

		currentHospital = hospitals[i][0].replace(" ", "+").strip('+')
		cidade = hospitals[i][1].replace(" ", "+").strip('+')
		estado = hospitals[i][2].replace(" ", "+").strip('+')
	
		print (">>>> CHAVE_API_KEY: ", chave_API_KEY)
	
		url = "https://maps.googleapis.com/maps/api/place/textsearch/xml?query="+currentHospital+cidade+estado+"&key="+API_KEY[chave_API_KEY]
		#url = "https://maps.googleapis.com/maps/api/place/textsearch/xml?query=HOSPITAL+REGIONAL+DO+JURUA&key=AIzaSyAb7AJfGi64tjj7l31qyAAV4OC-Tuuhs4c"
	
		response = requests.get(url)
		
		tree = ElementTree.fromstring(response.content)
		status = tree.findall("status")[0].text
		print ("Status elemento: ", status)
		#print ("ELEMENTO ROOT: ", tree.tag, tree.attrib)
		#print ("TAMANHO ATTRIB: ", len(tree.attrib))
		#print ("ADDRESS: ", tree[1].find('formatted_address').text)
		#print ("LATITUDE: ", tree[1].find('geometry').find('location').find('lat').text)
		#print ("LONGITUDE: ", tree[1].find('geometry').find('location').find('lng').text)

		# If the root element has no attributes
		if  ((status == "OK") and (hospitals[i][2] != "RJ")):
			data = {
					'nome': hospitals[i][0],
					'tipo': tipoHospital,			#geral ou especializado -> de acordo com planilha
					'localizacao': {
						'lat': float(tree[1].find('geometry').find('location').find('lat').text),
						'lng': float(tree[1].find('geometry').find('location').find('lng').text),
						'endereco': tree[1].find('formatted_address').text,
						'cidade': hospitals[i][1],
						'estado': hospitals[i][2]
					},
			}

			# Cria json object
			sent = json.dumps(data)
			jsonData = json.loads(sent)
			print "Dados: ", jsonData

			print "SALVANDO NO FIREBASE"
			# Salva no Firebase
			saveFirebase(firebase, jsonData)
			
			print "SALVANDO NO CSV"
			# Salva CSV
			saveCSV(arquivo_csv, jsonData)

			print "SALVANDO NO SQL"
			# Salva SQL
			saveSQL(arquivo_sql, jsonData)

			print "\n\n"


		elif ((status == "ZERO_RESULTS") or (status == "REQUEST_DENIED") or (status == "INVALID_REQUEST")):
			arquivo_naoSalvouBD.write(hospitals[i][0])
			arquivo_naoSalvouBD.write('\n')

		elif ((status == "OVER_QUERY_LIMIT")):
			arquivo_overquerylimit.write(hospitals[i][0])
			arquivo_overquerylimit.write('\n')
			
			if (chave_API_KEY > 5):
				chave_API_KEY = 0
			else: 
				chave_API_KEY = chave_API_KEY + 1

		arquivo_overquerylimit.close()
		arquivo_naoSalvouBD.close()
		#arquivo_csv.close()
		arquivo_sql.close()

		i = i + 1

	"""arquivo_overquerylimit.close()
	arquivo_naoSalvouBD.close()
	arquivo_csv.close()
	arquivo_sql.close()"""


#--------------------------------------------------------------------------------#
#																				 #
#--------------------------------------------------------------------------------#
def readExcelFile(input_file, sheet):

	xlsx_file = pd.ExcelFile(input_file, error_bad_lines=False)
	df = xlsx_file.parse(sheet)

	# Nome Hospital, Municipio, UF, Endereco
	hospitals = []
	listaIntermediaria = []
	for index, row in df.iterrows():
		if (not pd.isnull(row["Estabelecimento"])):
			listaIntermediaria.append(row["Estabelecimento"])
			listaIntermediaria.append(row["Municipio"])
			listaIntermediaria.append(row["UF"])
			hospitals.append(listaIntermediaria)
			listaIntermediaria = []

	return hospitals

#--------------------------------------------------------------------------------#
#																				 #
#--------------------------------------------------------------------------------#
def main():

	firebase = fb.FirebaseApplication('https://imergency-1478284581180.firebaseio.com/', None)

	#hospitalGeral = readExcelFile("Hospitais BRASIL - Abr2016.xlsx", "BRASIL - Hospital Geral")
	#tipoHospital = 'geral'
	hospitalGeral = readExcelFile("Hospitais BRASIL - Abr2016.xlsx", "BRASIL - Hospital Especializado")
	tipoHospital = 'especializado'

	print(">>>> QUANTIDADE HOSPITAIS: >>>> ", len(hospitalGeral))

	#index = -1
	for i in range(len(hospitalGeral)):
	#	print ("hosp: ", hospitalGeral[i], "\n")
		if (hospitalGeral[i][0] == "HOSPITAL DR FRANCISCO RIBEIRO ARANTES ITU"):
			index = i
			break
		#else:
		#	print ("hospital nao encontrado")

	#print ("indice: ", hospitalGeral[index+1])
	indexFrom = index + 1
	#indexFrom = 0

	requestAdress(hospitalGeral, firebase, tipoHospital, indexFrom)


#--------------------------------------------------------------------------------#
#																				 #
#--------------------------------------------------------------------------------#
if __name__ == '__main__':
	main()
