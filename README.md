# Microeconomic Chatbot

![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)

## Overview
Microeconomic Chatbot is an **open-source** chatbot designed for answering **microeconomics-related questions** using a **Retrieval-Augmented Generation (RAG) pipeline**. This project is a **demonstration of local LLM use cases**, built on **Kolosal AI** to showcase its capabilities in providing accurate and context-aware answers.

## Features
- 🚀 **Utilizes Kolosal AI** for retrieval and response generation (since we made Kolosal AI, this highlights our technology).
- 📚 **RAG-based Approach**: Uses document retrieval to enhance response quality.
- 🔄 **Runs Locally**: No external API calls required.
- 🖥️ **Docker-Ready**: Quick setup with Docker.
- 🆓 **Open Source**: Licensed under **Apache 2.0**, so anyone can use and modify it.

## Getting Started
Follow these steps to set up and run the chatbot using Docker.

### 1️⃣ Clone the Repository
```sh
git clone https://github.com/FarrelRamdhani/Microeconomic-Chatbot.git
cd microeconomic-chatbot
```

### 2️⃣ Build the Docker Image
```sh
docker build -t microeconomic-chatbot .
```

### 3️⃣ Run the Chatbot Container
```sh
docker run -p 8501:8501 microeconomic-chatbot
```

### 4️⃣ Access the Chatbot
Once the container is running, open your browser and go to:
```
http://localhost:8501/
```

## License
This project is licensed under the **Apache 2.0 License** - see the [LICENSE](LICENSE) file for details.

---

👥 **Contributions Welcome!** If you’d like to improve this chatbot, feel free to fork the repo and submit a pull request! 🚀