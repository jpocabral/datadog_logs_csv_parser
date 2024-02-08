import json
import pandas as pd

# Endereço do arquivo CSV
arquivo_csv = "C:/Users/p22.joao/Downloads/extract-2024-02-07T20_49_22.441Z.csv"


# Lê o arquivo novamente e cria um DataFrame Pandas
logs = pd.read_csv(arquivo_csv, usecols=['Message'])

first_line_content = str(logs.head(1))




# Identificando possível Trace ID ou Step no conteúdo dos logs
if "Trace ID" or "Step" in first_line_content :
    logs['Trace ID'] = logs['Message'].str.split(r'\[Trace ID: ([^\]]+)\]', expand=True)[1]
    logs['Message'] = logs['Message'].str.split(r'\[Trace ID: ([^\]]+)\]', expand=True)[2]
    logs['Step'] = logs['Message'].str.split(r'\[Step: (\d+)\]', expand=True)[1]
    logs['Message'] = logs['Message'].str.split(r'\[Step: (\d+)\]', expand=True)[2]

# Identificando possível Body no conteúdo dos logs    
if '"Body":' or "'Body':" in first_line_content:
    # Extraindo o Body JSON:
    logs['Body'] = (logs['Message'].str.split('"Body":', expand=True)[1])    # Pega tudo a direita de '"Body":'
    logs['Body'] = (logs['Body'].str.split('","Md5OfBody"', expand=True)[0]) # Pega tudo a esquerda de '","Md5OfBody"'
    # Corrigindo caracteres que causam quebra na string do JSON
    logs['Body'] = logs['Body'].str.replace('\\"', '"').str.replace('\\n', '').str.replace('"{', '{').str.replace('}"', '}').str.replace('//', '\/\/') 
    # Converte String JSON para JSON
    logs['Body'] = logs['Body'].apply(json.loads)
    # Convertendo a estrutura de 'Chave e Valor' do JSON para 'Coluna e Linha' e adicionando as novas colunas ao DataFrame logs 
    logs = logs.assign(**(pd.json_normalize(logs['Body']))) 
    # Deletando as colunas usadas no processo
    del logs['Message'] # Deletando a coluna Message contendo o Body e demais strings
    del logs['Body'] # Deletando a coluna Body


# Salvando arquivo no formado .xlsx do Excel
try:
    logs.to_excel("Logs.xlsx", index=False)
except PermissionError:
    print("\nPermission Denied, please close the file or check write permissions!")


# Define a search function
def search_string(s, search):
    return search in str(s).lower()

# Search for the string 'al' in all columns
# mask = df.apply(lambda x: x.map(lambda s: search_string(s, 'al')))

# Filter the DataFrame based on the mask
# filtered_df = df.loc[mask.any(axis=1)]
# print(filtered_df)