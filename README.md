Certamente! Aqui está a seção de configuração em português no README.md, com base nas informações fornecidas:

# Middleware FastAPI para WhatsApp com Integração Twilio, Speech-to-Text e Chatbot

## Visão Geral

Este projeto implementa um middleware FastAPI para WhatsApp usando Twilio que lida com mensagens recebidas, tanto de texto quanto de áudio, por meio de webhook. Para mensagens de áudio, o middleware usa um modelo Whisper ou um modelo WAV2WAC personalizado para Speech-to-Text (STT). Os dados de texto são então processados e, se aplicável, enviados para um serviço de chatbot.

## Pré-requisitos

Certifique-se de ter o seguinte instalado e configurado antes de executar o middleware:

- [Python](https://www.python.org/) e [pip](https://pip.pypa.io/en/stable/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Conta Twilio](https://www.twilio.com/) com um Sandbox do WhatsApp configurado
- Modelo Speech-to-Text (STT) (Whisper ou WAV2WAC personalizado)
- Serviço de Chatbot

## Instalação

1. Clone o repositório:

    ```bash
    git clone https://github.com/caiomagri/whatsapp_middleware.git
    cd whatsapp-middleware
    ```

2. Configure o middleware:

    - Crie um arquivo `.env` e adicione suas credenciais do Twilio, STT e Chatbot.

## Configuração

Atualize o arquivo `.env` com as seguintes configurações:

```bash
# Configuração Twilio
TWILIO_ACCOUNT_SID=sua_conta_twilio_sid
TWILIO_AUTH_TOKEN=seu_token_twilio
TWILIO_WHATSAPP_NUMBER=seu_numero_whatsapp_twilio

# Configuração do Modelo de Transcrição de Áudio
AUDIO_TRANSCRIBE_MODEL=

# Configuração do Modelo Whisper (se estiver usando Whisper)
WHISPER_LOAD_MODEL=small
WHISPER_DEVICE=cpu
WHISPER_COMPUTE_TYPE=int8

# Configuração do Chatbot
CHATBOT_ENDPOINT=http://127.0.0.1:8001/chatbot
```

Substitua `sua_conta_twilio_sid`, `seu_token_twilio`, e `seu_numero_whatsapp_twilio` pelas informações reais de sua conta Twilio. Certifique-se de que o endpoint do chatbot (`CHATBOT_ENDPOINT`) está configurado corretamente para apontar para o serviço de chatbot que você está utilizando.

## Uso

1. Inicie o middleware:

    ```bash
    docker-compsoe up 
    ```

2. Configure seu Sandbox do WhatsApp Twilio para usar a URL gerada pelo FastAPI.

3. Envie mensagens de texto ou áudio para seu número do WhatsApp Twilio, e o middleware irá processar e encaminhar os dados para os serviços apropriados.

## Notas Adicionais

- Certifique-se de que seu serviço STT e Chatbot estejam configurados corretamente e acessíveis a partir do middleware.

- Trate erros e casos específicos de acordo com os requisitos de sua aplicação.

- Para uso em produção, proteja o middleware com autenticação adequada e considere implantá-lo em um servidor confiável.
