import openai

client = openai.OpenAI(
    api_key="sk-api-qHlVsSmhihQ-ABnH3KT5uRYPB8UfeNLXFHXpCXaWaky42fCpZAjko3nnd_ij1hdzlpFlqEgeLtB6-3Ufvs0_IkEKWexkiAQJaFUKVRzpUm2uF7lQpUHEook",
    base_url="https://api.minimax.chat/v1" # 或者使用国内域名 https://api.minimaxi.chat/v1
)

response = client.chat.completions.create(
    model="MiniMax-M2.5", # 注意：部分平台可能需要写成 "minimax/m2.5"
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "帮我写一段 Python 快速排序代码，并详细解释逻辑。"}
    ],
    # M2.5 支持思维链显示，如果是在支持的客户端上可以看到推理过程
)

print(response.choices[0].message.content)