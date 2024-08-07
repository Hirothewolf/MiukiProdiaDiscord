Modularização do Código:

O bot foi completamente modularizado, separando as funcionalidades em diferentes módulos para facilitar a manutenção e a escalabilidade.
Criação de Módulos Independentes:

Comandos de Geração de Imagens:

/facerestorer: Restaura rostos em imagens usando a API Prodia. (W.I.P)
/faceswap: Troca rostos entre imagens. (W.I.P)
/photomaker: Cria fotos a partir de descrições. (W.I.P)
/sdxl_img2img: Gera imagens a partir de outras imagens usando Stable Diffusion XL. (W.I.P)
/sdxl_inpaint: Permite pintura digital em imagens usando Stable Diffusion XL. (W.I.P)
/sdxlgen: Gera imagens a partir de descrições usando Stable Diffusion XL.
/sd1x_inpaint: Permite pintura digital em imagens usando Stable Diffusion 1.x. (W.I.P)
/sd1x_gen: Gera imagens a partir de descrições usando Stable Diffusion 1.x.
/sd1x_controlnet: Integra ControlNet com geração de imagens usando Stable Diffusion 1.x. (W.I.P)
/sd1x_img2img: Gera imagens a partir de outras imagens usando Stable Diffusion 1.x. (W.I.P)
/lora_sdxl: Gera imagens usando modelos LORA com Stable Diffusion XL.
/lora_sd1x: Gera imagens usando modelos LORA com Stable Diffusion 1.x.
/models_sd1x: Gerencia modelos de Stable Diffusion 1.x.
/models_sdxl: Gerencia modelos de Stable Diffusion XL.
/upscale: Realiza upscale de imagens usando a API Prodia.
Filtragem de Conteúdo:

/filtronsfw_sd1x: Ativa ou desativa o filtro anti-NSFW para geração de imagens.
/filtronsfw_sdxl: Ativa ou desativa o filtro anti-NSFW para geração de imagens.
Adição de Arquivo de Configuração:

config.py: Centraliza a configuração do bot, incluindo a chave da API (API_KEY) e outras configurações relevantes.
Sistema de Cache para Imagens:

Implementado um sistema de cache para armazenar as imagens geradas, permitindo operações subsequentes sem a necessidade de reprocessamento.
Verificações e Failsafes:

Adicionados failsafes para detectar e notificar o usuário quando uma imagem fornecida é muito grande, tanto para URLs quanto para uploads de arquivos.
Verificação do tamanho do conteúdo das URLs antes de processar imagens para garantir que não excedam o limite permitido.
Verificação do tamanho das imagens enviadas como arquivos para garantir que não excedam 25 milhões de pixels.
Melhorias de Feedback ao Usuário:

Melhorias na comunicação de erros e no feedback ao usuário, informando claramente sobre problemas como URLs inválidas, arquivos de imagem muito grandes ou formatos de imagem não suportados.
Integração de Embeds:

Todos os comandos agora utilizam embeds do Discord para exibir resultados de forma clara e organizada, incluindo detalhes como modelo usado, fator de resize, e outras informações relevantes.
Controle de Permissões:

Adicionados controles de permissão para ações sensíveis, garantindo que apenas o usuário que solicitou a operação ou administradores possam deletar imagens.
Correções de Bugs:

Correção de um erro HTTP 400 ao tentar realizar upscale de imagens muito grandes.
Ajustes nas verificações de imagens para garantir compatibilidade com diferentes formatos de imagem e tamanhos de arquivo.
