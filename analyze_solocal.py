import os
import pandas as pd
import openai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

def query_gpt(row,counter):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k-0613",
            messages=[
                {"role": "system", "content": """
                 Voici la description d'une entreprise :


                 Solocal propose des solutions digitales pour les entreprises locales, incluant la création de sites Internet, la publicité digitale, la gestion de la présence en ligne, et des services de messagerie instantanée et de prise de rendez-vous en ligne. Ils visent à optimiser la visibilité des entreprises sur Internet, les aider à gérer leur réputation en ligne, et à améliorer l'interaction avec leurs clients. Solocal s'adresse aux TPE/PME, réseaux d'enseignes, ainsi qu'au secteur public et collectivités.

                 Je vais te donner une description d'appel d'offre et tu dois me dire si cela correspond a ce que fait cette entreprise. Tu ne dois repondre que TRUE ou FALSE rien de plus"""},
                {"role": "user", "content": row}
            ]
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        return f"Error: {e}"

df = pd.read_csv("api_data.csv", sep=';')
df_unique = df.drop_duplicates(subset=["objet"]).copy()
counter = 1
for index, row in df_unique.iterrows():
    df_unique.at[index, "gpt_response"] = query_gpt(row["objet"], counter)
    counter += 1
    print(counter)
df_unique.to_csv("api_data_with_responses.csv", index=False, sep=';')

df = pd.read_csv("api_data_simap.csv")
df_unique = df.drop_duplicates(subset=["description"]).copy()
for index, row in df_unique.iterrows():
    df_unique.at[index, "gpt_response"] = query_gpt(row["description"], counter)
    counter += 1
    print(counter)
df_unique.to_csv("api_data_with_responses_simap.csv", index=False)

df1 = pd.read_csv('api_data_with_responses.csv', sep=';')
df2 = pd.read_csv('api_data_with_responses_simap.csv', sep=',')
df1_transformed = df1[['idweb', 'objet', 'gpt_response', 'url_pdf']].copy()
df1_transformed.columns = ['id', 'desc', 'gpt_responses', 'url_pdf']
df1_transformed['country'] = 'FRANCE'
df2_transformed = df2[['id', 'description', 'gpt_response']].copy()
df2_transformed.columns = ['id', 'desc', 'gpt_responses']
df2_transformed['url_pdf'] = ''
df2_transformed['country'] = 'SUISSE'
df_fusion = pd.concat([df1_transformed, df2_transformed], ignore_index=True)
df_fusion.to_csv('data/api_data_fusion_solocal.csv', index=False)