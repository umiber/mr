# -*- coding: utf-8 -*-
"""analise_campanha_comentarios.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/15KNt6A2mzSJjfdw5Jgt0sVOh8cncQ3QM

# 📘 Análise de Campanhas com Comentários
"""



# 🔼 1. Upload da planilha Excel
from google.colab import files
uploaded = files.upload()

# 📥 2. Leitura da planilha e das abas
import pandas as pd

file_name = list(uploaded.keys())[0]
xls = pd.ExcelFile(file_name)

df_campanha = pd.read_excel(xls, "Campanha")
df_post = pd.read_excel(xls, "Post")

print("✅ Dados carregados com sucesso!")
print(f"▶ Campanha: {df_campanha.shape[0]} linhas")
print(f"▶ Post: {df_post.shape[0]} linhas")

# 👀 3. Visualização inicial dos dados
display(df_campanha.head())
display(df_post.head())

# 💬 4. Análise de comentários e sentimentos
!pip install -q transformers
from transformers import pipeline

# Cria pipeline de sentimento
sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")

# Aplica análise nos primeiros 100 comentários (por performance)
comentarios = df_post["Comentário"].dropna().astype(str).tolist()[:100]
sentimentos = sentiment_analyzer(comentarios)

# Cria DataFrame com resultados
import pandas as pd
df_sentimento = pd.DataFrame(sentimentos)
df_sentimento["Comentário"] = comentarios

# Exibe resultados
df_sentimento.head(10)

# 5. Bloco complementar: Gráfico de barras da distribuição de sentimentos

import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import numpy as np


# Converte para DataFrame a coluna de sentimentos
df_post["Sentimento"] = [s["label"].capitalize() for s in sentimentos]

# Conta quantos comentários para cada sentimento
sent_counts = df_post["Sentimento"].value_counts().reset_index()
sent_counts.columns = ["Sentimento", "Quantidade"]

# Gráfico
# Coordenadas
x = np.arange(len(sent_counts))
y = np.zeros_like(x)
z = np.zeros_like(x)
dx = np.ones_like(x) * 0.5
dy = np.ones_like(x) * 0.5
dz = sent_counts["Quantidade"].values

# Criação da figura
fig = plt.figure(figsize=(10, 6))
ax = fig.add_subplot(111, projection='3d')

# Barras 3D
bars = ax.bar3d(x, y, z, dx, dy, dz, color='royalblue', alpha=0.8)

# Rótulos e layout
ax.set_xticks(x)
ax.set_xticklabels(sent_counts["Sentimento"])
ax.set_xlabel('Sentimento')
ax.set_ylabel('')
ax.set_zlabel('Quantidade')
ax.set_title('📊 Distribuição de Sentimentos nos Comentários (3D)')

# Adiciona rótulo com valor no topo de cada barra
for i in range(len(dz)):
    ax.text(x[i], y[i], dz[i] + 0.5, str(dz[i]), ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.show()

# 6. Geração de síntese dos comentários em inglês com transformers
!pip install -q transformers sentencepiece
from transformers import pipeline

# Carrega o modelo de sumarização
resumidor = pipeline("summarization", model="facebook/bart-large-cnn")

# Junta os comentários em um único texto
comentarios = df_post["Comentário"].dropna().astype(str).tolist()
texto_unico = " ".join(comentarios)

# Divide o texto em blocos menores (~500 caracteres por bloco)
blocos = []
tamanho_bloco = 500
for i in range(0, len(texto_unico), tamanho_bloco):
    blocos.append(texto_unico[i:i + tamanho_bloco])

# Gera resumos parciais
resumos_parciais = []
for i, bloco in enumerate(blocos):
    try:
        resumo = resumidor(bloco, max_length=100, min_length=30, do_sample=False)[0]['summary_text']
        resumos_parciais.append(resumo)
    except Exception as e:
        print(f"Erro ao resumir bloco {i}: {e}")

# Junta os resumos parciais e gera uma síntese final
texto_resumo_parcial = " ".join(resumos_parciais)
sintese_final = resumidor(texto_resumo_parcial, max_length=130, min_length=30, do_sample=False)[0]['summary_text']

# Exibe o resultado em HTML com quebra de linha
from IPython.display import display, HTML

display(HTML(f"""
<div style='background-color:#f9f9f9; border:1px solid #ccc; padding:20px; border-radius:5px; font-family:Arial; line-height:1.6; max-width:1000px;'>
<strong>📘 Insight baseado nos comentários:</strong><br><br>
{sintese_final}
</div>
"""))

# 📊 7. Gráficos por Sexo, Idade, Likes
import seaborn as sns
import matplotlib.pyplot as plt

# Distribuição de sexo
sns.countplot(data=df_post, x="Sexo")
plt.title("Distribuição por Sexo")
plt.show()

# Likes por sexo
sns.boxplot(data=df_post, x="Sexo", y="Likes")
plt.title("Likes por Sexo")
plt.show()

# Likes por faixa etária (binned)
df_post["FaixaEtaria"] = pd.cut(df_post["Idade"], bins=[0, 20, 30, 40, 50, 100], labels=["<20", "21–30", "31–40", "41–50", "50+"])
sns.boxplot(data=df_post, x="FaixaEtaria", y="Likes")
plt.title("Likes por Faixa Etária")
plt.show()

import os
import ipywidgets as widgets
from IPython.display import display, clear_output

def export_to_pdf(btn):
    clear_output()
    print("📝 Gerando PDF...")
    os.system("jupyter nbconvert --to pdf analise_campanha_comentarios.ipynb")
    print("✅ PDF gerado com sucesso!")

button = widgets.Button(description="📄 Gerar PDF da análise")
button.on_click(export_to_pdf)
display(button)