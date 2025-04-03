# -*- coding: utf-8 -*-
"""EmotionClassification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1rA9GGBX9JXQwLQ_-1uwEkMPciJark4WD

# Emotion Classification (text vs audio)

### Introduction

Artificial intelligence is increasingly used to interpret human emotion in areas where communication plays a critical role—such as healthcare, governance, and public leadership. Many of these systems rely on a single input modality, typically either text or speech, to detect emotional cues. However, emotion is a multimodal phenomenon, conveyed not just through words but also through tone, pacing, and emphasis. This project addresses the question:

"How do text-based and speech-based models interpret the same emotional message differently?"

Using political speeches as the core dataset—rich in rhetorical and emotional expression—we compare AI model predictions from both text transcripts and speech audio. This work seeks to understand what emotional nuance is preserved, lost, or transformed when only one modality is used, with broader implications for emotion-aware AI in global communication, governance, and social technologies.

### Problem Statement

In political discourse, the way a message is delivered can be just as important—if not more so—than the words themselves. A leader may speak words of unity while delivering them in a cold, monotone voice, or express defiance with carefully chosen polite phrasing delivered in a passionate, energized tone. This distinction between what is said (text) and how it is said (speech) poses a unique challenge for emotion classification systems.

Most current emotion detection models are unimodal—they analyze either text or speech, not both. As a result, these models risk misinterpreting emotional intent if they lack access to vocal cues like pitch, emphasis, or rhythm. This limitation is particularly significant in political speeches, where emotional messaging is a tool for persuasion, leadership, and public mobilization.

If AI models fail to recognize these nuances, they may misclassify emotional tone, overlook persuasive intent, or fail to detect deeper sentiment behind diplomatic language. This raises key questions about the design of emotion-aware systems and how different input modalities shape emotional interpretation.

By comparing predictions from text-based and speech-based models on the same political segments, this project explores the extent to which emotional interpretation varies by modality—and what that means for designing emotionally intelligent technologies in high-stakes communication environments.

### Methodology

We selected three publicly available speeches by global leaders:

Javier Milei (Argentina) – UN General Assembly (Ideological/Economic)

Ursula von der Leyen (EU) – COP28 Climate Summit (Environmental)

Dr. Tedros Adhanom Ghebreyesus (WHO) – WHO Executive Board (Healthcare)

Each speech was collected in two formats: full audio/video and official transcript, allowing for paired multimodal analysis.

1. SamLowe/roberta-base-go_emotions

A transformer model based on RoBERTa and fine-tuned on Google’s GoEmotions dataset. This dataset contains 27 nuanced emotions plus a neutral label.

Why it was used: It supports multi-label classification, meaning it can detect multiple emotions in a single segment (e.g., sadness + fear).

How it worked: The model output probabilities for each emotion, and we applied a threshold (e.g., 0.5) to determine which labels were considered present.

2. j-hartmann/emotion-english-distilroberta-base

A smaller and faster DistilRoBERTa model trained on the same GoEmotions dataset.

Difference from baseline: Unlike the SamLowe model, this one outputs a single most likely emotion for each input, offering a simpler and more focused classification.

Purpose: It allowed us to see how model size and architecture affect interpretation of emotional tone.

3. Sentiment Analysis and Lexicon Based Emotion

Used cardiffnlp/twitter-roberta-base-sentiment to classify the overall sentiment of each segment as positive, negative, or neutral. This model is based on RoBERTa and trained on a large dataset of tweets, making it suitable for detecting the general emotional tone of informal and formal text. incorporated the NRCLex library, based on the NRC Emotion Lexicon, which maps words to eight core emotions (anger, fear, joy, trust, sadness, disgust, surprise, anticipation) and two sentiment labels (positive, negative).

Why it was used: Lexicon methods provide a rule-based, interpretable benchmark. They don’t require training and are useful for highlighting differences between statistical models and dictionary lookups.

# Ideological and Economic (Javier Milei)

In his 2024 speech at the United Nations General Assembly, Argentine President Javier Milei delivers a passionate and ideologically charged critique of collectivism and global institutions that, in his view, perpetuate its values. He argues that Argentina has suffered for over a century under collectivist policies—such as socialism, statism, and economic interventionism—which he claims have led to poverty, stagnation, and social decay. Presenting himself as a non-traditional politician and a libertarian economist, Milei positions Argentina’s new direction as a bold break from the past. He defends capitalism as the only system capable of fostering true freedom, prosperity, and innovation, insisting that individual liberty and limited government are essential for national success. Throughout his speech, he warns that international frameworks like the UN’s Agenda 2030 promote dangerous collectivist ideologies on a global scale. By framing Argentina as a model for ideological resistance and economic reform, Milei calls on other nations to reject these ideas and embrace liberty, concluding with his signature phrase: “¡Viva la libertad, carajo!” (“Long live freedom, damn it!”). His tone throughout is assertive and unapologetically combative, signaling a radical shift in Argentina’s role on the world stage.

## Text Emotion Classification

#### SamLowe/roberta-base-go_emotions
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("SamLowe/roberta-base-go_emotions")
model = AutoModelForSequenceClassification.from_pretrained("SamLowe/roberta-base-go_emotions")

# Load the speech transcript
with open('milei_speech.txt', 'r', encoding='utf-8') as file:
    speech_text = file.read()

# Split speech into paragraphs
segments = speech_text.split('\n\n')  # Adjust the delimiter as needed

import torch
import torch.nn.functional as F

# Get model's label mappings
id2label = model.config.id2label

results = []

for segment in segments:
    if segment.strip():  # Ensure the segment is not empty
        # Tokenize the segment
        inputs = tokenizer(segment, return_tensors="pt", truncation=True, padding=True)
        # Get model predictions
        with torch.no_grad():
            logits = model(**inputs).logits
        # Apply sigmoid to get probabilities
        probs = F.sigmoid(logits.squeeze())
        # Filter labels with probability above a certain threshold (e.g., 0.5)
        threshold = 0.5
        predicted_labels = [id2label[i] for i, prob in enumerate(probs) if prob > threshold]
        # Store results
        results.append({
            'Segment': segment,
            'Predicted Emotions': predicted_labels,
            'Emotion Probabilities': {id2label[i]: prob.item() for i, prob in enumerate(probs)}
        })

# Display results
for result in results:
    print(f"Segment: {result['Segment']}")
    print(f"Predicted Emotions: {result['Predicted Emotions']}")
    print(f"Emotion Probabilities: {result['Emotion Probabilities']}")
    print('-' * 50)

"""#### j-hartmann/emotion-english-distilroberta-base"""

# Load the DistilRoBERTa-based emotion model
emotion_model_name = "j-hartmann/emotion-english-distilroberta-base"
emotion_tokenizer = AutoTokenizer.from_pretrained(emotion_model_name)
emotion_model = AutoModelForSequenceClassification.from_pretrained(emotion_model_name)

# Get emotion label map
id2label = emotion_model.config.id2label
label_list = list(id2label.values())

# Emotion classification function using DistilRoBERTa
def get_distilroberta_emotions(texts):
    results = []
    for text in texts:
        inputs = emotion_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = emotion_model(**inputs).logits
        probs = torch.nn.functional.softmax(logits, dim=-1).numpy()[0]
        top_emotion = label_list[np.argmax(probs)]
        result = {
            "text": text,
            "top_emotion": top_emotion
        }
        for label, prob in zip(label_list, probs):
            result[label] = round(prob, 4)
        results.append(result)
    return pd.DataFrame(results)

# Run DistilRoBERTa on Javier speech
javier_emotion_df = get_distilroberta_emotions(javier_segments)

# Preview
print("Javier Transcript Emotion Output:")
display(javier_emotion_df.head())

"""#### Sentiment Analysis"""

!pip install nrclex

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from nrclex import NRCLex
import torch
import pandas as pd
import numpy as np
from collections import Counter

# Load Javier Transcript
with open("milei_speech.txt", "r", encoding="utf-8") as file:
    javier_transcript = file.read()

# Segment transcript into meaningful chunks
javier_segments = [seg.strip() for seg in javier_transcript.split("\n") if len(seg.strip()) > 30]

# Load sentiment analysis model (3-class)
sentiment_model_name = "cardiffnlp/twitter-roberta-base-sentiment"
sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)
sentiment_labels = ['negative', 'neutral', 'positive']

# Sentiment analysis function
def get_sentiment_scores(texts):
    scores = []
    for text in texts:
        inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = sentiment_model(**inputs).logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1).numpy()[0]
        sentiment = sentiment_labels[np.argmax(probabilities)]
        scores.append({
            "text": text,
            "negative": round(probabilities[0], 3),
            "neutral": round(probabilities[1], 3),
            "positive": round(probabilities[2], 3),
            "sentiment": sentiment
        })
    return pd.DataFrame(scores)

# Lexicon-based emotion function
def get_nrc_emotions(texts):
    import nltk  # Import nltk here

    # Download required NLTK data
    nltk.download('punkt_tab', quiet=True)  # Download punkt_tab data, suppress download messages
    nltk.download('punkt', quiet=True)      # Download punkt data, suppress download messages

    results = []
    for text in texts:
        emotion_obj = NRCLex(text)
        raw_scores = emotion_obj.raw_emotion_scores
        top_emotions = emotion_obj.top_emotions
        result = {
            "text": text,
            "raw_scores": raw_scores,
            "top_emotions": top_emotions
        }
        result.update(Counter(raw_scores))
        results.append(result)
    return pd.DataFrame(results)

# Run both analyses
javier_sentiment_df = get_sentiment_scores(javier_segments)
javier_lexicon_df = get_nrc_emotions(javier_segments)

# Merge dataframes on text segment
javier_combined_df = pd.merge(javier_sentiment_df, javier_lexicon_df, on="text")

# Preview the combined data
javier_combined_df.head()

"""### Evaluation Analysis (needs work)"""

import pandas as pd
import matplotlib.pyplot as plt

# Convert results to DataFrame
df = pd.DataFrame(results)

# Extract the most probable emotion for each segment
df['Top Emotion'] = df['Emotion Probabilities'].apply(lambda x: max(x, key=x.get) if x else None)

# Now you can use 'Top Emotion' column for plotting
emotion_counts = df['Top Emotion'].value_counts()
emotion_counts.plot(kind='bar', figsize=(10, 5), title="Emotion Frequency in Speech")
plt.xlabel("Emotion")
plt.ylabel("Count")
plt.show()

# Plot emotions across segments
df['Segment #'] = range(len(df))
# Convert 'Top Emotion' to categorical and assign numerical codes
df['Top Emotion Code'] = pd.Categorical(df['Top Emotion']).codes

# Plot using the numerical codes
df.set_index('Segment #')['Top Emotion Code'].plot(marker='o', title="Emotion Flow Across Speech", figsize=(12, 4))
plt.ylabel("Emotion Code") # Update y-axis label
plt.yticks(df['Top Emotion Code'].unique(), df['Top Emotion'].unique()) # Set y-ticks to original emotion labels
plt.show()

"""# Environmental (Ursula von der Leyen)

In her 2023 speech at the COP28 Climate Summit in Dubai, European Commission President Ursula von der Leyen delivers a focused and forward-looking address centered on urgent global action against climate change. Emphasizing the disproportionate role of energy production—responsible for 75% of global greenhouse gas emissions—she calls on the international community to commit to tripling renewable energy capacity and doubling energy efficiency by 2030. Framing these goals as both achievable and essential, von der Leyen highlights the dramatic reduction in the cost of solar energy as proof that sustainable development is within reach. She stresses the importance of collective accountability, advocating for quantifiable, measurable targets to ensure real progress. Her speech is grounded in pragmatism and optimism, positioning the European Union as a leader in the global green transition. Rather than warning of catastrophe, von der Leyen presents climate action as an opportunity for innovation, economic growth, and shared responsibility. Her tone is assertive yet diplomatic, appealing to both urgency and hope as she urges world leaders to unite around a transformative energy agenda for the planet’s future.

## Text Emotion Classification

#### SamLowe/roberta-base-go_emotions
"""

with open("von_der_leyen_cop28.txt", "r", encoding="utf-8") as file:
    transcript = file.read()

segments = [seg.strip() for seg in transcript.split("\n") if len(seg.strip()) > 30]

from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("SamLowe/roberta-base-go_emotions")
model = AutoModelForSequenceClassification.from_pretrained("SamLowe/roberta-base-go_emotions")

# Get model's label mappings
id2label = model.config.id2label

results = []

for segment in segments:
    if segment.strip():  # Ensure the segment is not empty
        # Tokenize the segment
        inputs = tokenizer(segment, return_tensors="pt", truncation=True, padding=True)
        # Get model predictions
        with torch.no_grad():
            logits = model(**inputs).logits
        # Apply sigmoid to get probabilities
        probs = F.sigmoid(logits.squeeze())
        # Filter labels with probability above a certain threshold (e.g., 0.5)
        threshold = 0.5
        predicted_labels = [id2label[i] for i, prob in enumerate(probs) if prob > threshold]
        # Store results
        results.append({
            'Segment': segment,
            'Predicted Emotions': predicted_labels,
            'Emotion Probabilities': {id2label[i]: prob.item() for i, prob in enumerate(probs)}
        })

# Display results
for result in results:
    print(f"Segment: {result['Segment']}")
    print(f"Predicted Emotions: {result['Predicted Emotions']}")
    print(f"Emotion Probabilities: {result['Emotion Probabilities']}")
    print('-' * 50)

"""#### j-hartmann/emotion-english-distilroberta-base"""

# Load and segment von der Leyen transcript
with open("von_der_leyen_cop28.txt", "r", encoding="utf-8") as file:
    von_transcript = file.read()
von_segments = [seg.strip() for seg in von_transcript.split("\n") if len(seg.strip()) > 30]

# Load the DistilRoBERTa-based emotion model
emotion_model_name = "j-hartmann/emotion-english-distilroberta-base"
emotion_tokenizer = AutoTokenizer.from_pretrained(emotion_model_name)
emotion_model = AutoModelForSequenceClassification.from_pretrained(emotion_model_name)

# Get emotion label map
id2label = emotion_model.config.id2label
label_list = list(id2label.values())

# Emotion classification function using DistilRoBERTa
def get_distilroberta_emotions(texts):
    results = []
    for text in texts:
        inputs = emotion_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = emotion_model(**inputs).logits
        probs = torch.nn.functional.softmax(logits, dim=-1).numpy()[0]
        top_emotion = label_list[np.argmax(probs)]
        result = {
            "text": text,
            "top_emotion": top_emotion
        }
        for label, prob in zip(label_list, probs):
            result[label] = round(prob, 4)
        results.append(result)
    return pd.DataFrame(results)

# Run DistilRoBERTa on von der Leyen speech
von_emotion_df = get_distilroberta_emotions(von_segments)

# Preview
print("Von der Leyen Transcript Emotion Output:")
display(von_emotion_df.head())

"""#### Sentiment Analysis"""

# Load de Leyen Transcript
with open("von_der_leyen_cop28.txt", "r", encoding="utf-8") as file:
    leyen_transcript = file.read()

# Segment transcript into meaningful chunks
leyen_segments = [seg.strip() for seg in leyen_transcript.split("\n") if len(seg.strip()) > 30]

# Load sentiment analysis model (3-class)
sentiment_model_name = "cardiffnlp/twitter-roberta-base-sentiment"
sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)
sentiment_labels = ['negative', 'neutral', 'positive']

# Sentiment analysis function
def get_sentiment_scores(texts):
    scores = []
    for text in texts:
        inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = sentiment_model(**inputs).logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1).numpy()[0]
        sentiment = sentiment_labels[np.argmax(probabilities)]
        scores.append({
            "text": text,
            "negative": round(probabilities[0], 3),
            "neutral": round(probabilities[1], 3),
            "positive": round(probabilities[2], 3),
            "sentiment": sentiment
        })
    return pd.DataFrame(scores)

# Lexicon-based emotion function
def get_nrc_emotions(texts):
    import nltk  # Import nltk here

    # Download required NLTK data
    nltk.download('punkt_tab', quiet=True)  # Download punkt_tab data, suppress download messages
    nltk.download('punkt', quiet=True)      # Download punkt data, suppress download messages

    results = []
    for text in texts:
        emotion_obj = NRCLex(text)
        raw_scores = emotion_obj.raw_emotion_scores
        top_emotions = emotion_obj.top_emotions
        result = {
            "text": text,
            "raw_scores": raw_scores,
            "top_emotions": top_emotions
        }
        result.update(Counter(raw_scores))
        results.append(result)
    return pd.DataFrame(results)

# Run both analyses
leyen_sentiment_df = get_sentiment_scores(leyen_segments)
leyen_lexicon_df = get_nrc_emotions(leyen_segments)

# Merge dataframes on text segment
leyen_combined_df = pd.merge(leyen_sentiment_df, leyen_lexicon_df, on="text")

# Preview the combined data
leyen_combined_df.head()

"""# Healthcare (Dr. Tedros Adhanom Ghebreyesus)

In his 2025 speech at the 156th session of the World Health Organization’s Executive Board in Geneva, Director-General Dr. Tedros Adhanom Ghebreyesus delivers a comprehensive and forward-thinking address focused on the state of global health and the need for renewed international collaboration. Reflecting on the WHO’s response to over 50 emergencies in the past year—including conflicts, disease outbreaks, and natural disasters—Dr. Tedros emphasizes the critical importance of preparedness and rapid response in saving lives. He draws special attention to maternal and newborn health, celebrating measurable progress in countries like Tanzania, Pakistan, and Malawi, while announcing that World Health Day 2025 will spotlight maternal health as a global priority. Dr. Tedros frames the challenges of the post-pandemic era not as setbacks but as opportunities for health systems to become more resilient and equitable. His message is one of cautious optimism, grounded in the belief that trust, cooperation, and sustained investment in public health infrastructure are essential to prevent avoidable suffering. Delivered with calm urgency, his tone reflects both concern for ongoing challenges and confidence in the global community’s capacity to overcome them through shared responsibility.

## Text Emotion Classification

#### SamLowe/roberta-base-go_emotions
"""

# Read the transcript
with open("tedros_speech.txt", "r", encoding="utf-8") as file:
    transcript = file.read()

# Segment the transcript
segments = [seg.strip() for seg in transcript.split("\n") if len(seg.strip()) > 30]

# Load model and tokenizer
model_name = "SamLowe/roberta-base-go_emotions"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Get id2label mapping
id2label = model.config.id2label

results = []

for segment in segments:
    if segment.strip():
        inputs = tokenizer(segment, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = model(**inputs).logits
        probs = F.sigmoid(logits.squeeze())
        predicted_labels = [id2label[i] for i, prob in enumerate(probs) if prob > threshold]

        results.append({
            'Segment': segment,
            'Predicted Emotions': predicted_labels,
            'Emotion Probabilities': {id2label[i]: round(prob.item(), 3) for i, prob in enumerate(probs)}
        })

# Display the results
for result in results:
    print(f"Segment: {result['Segment']}")
    print(f"Predicted Emotions: {result['Predicted Emotions']}")
    print(f"Emotion Probabilities: {result['Emotion Probabilities']}")
    print('-' * 50)

"""#### j-hartmann/emotion-english-distilroberta-base"""

# Load and segment Healthcare transcript (Tedros speech)
with open("tedros_speech.txt", "r", encoding="utf-8") as file:
    tedros_transcript = file.read()
tedros_segments = [seg.strip() for seg in tedros_transcript.split("\n") if len(seg.strip()) > 30]

# Load the DistilRoBERTa-based emotion model
emotion_model_name = "j-hartmann/emotion-english-distilroberta-base"
emotion_tokenizer = AutoTokenizer.from_pretrained(emotion_model_name)
emotion_model = AutoModelForSequenceClassification.from_pretrained(emotion_model_name)

# Get emotion label map
id2label = emotion_model.config.id2label
label_list = list(id2label.values())

# Emotion classification function using DistilRoBERTa
def get_distilroberta_emotions(texts):
    results = []
    for text in texts:
        inputs = emotion_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = emotion_model(**inputs).logits
        probs = torch.nn.functional.softmax(logits, dim=-1).numpy()[0]
        top_emotion = label_list[np.argmax(probs)]
        result = {
            "text": text,
            "top_emotion": top_emotion
        }
        for label, prob in zip(label_list, probs):
            result[label] = round(prob, 4)
        results.append(result)
    return pd.DataFrame(results)

# Run DistilRoBERTa on the Tedros healthcare speech
tedros_emotion_df = get_distilroberta_emotions(tedros_segments)

# Preview
print("Tedros Healthcare Transcript Emotion Output:")
display(tedros_emotion_df.head())

"""#### Sentiment Analysis"""

# Load Tedros Transcript
with open("tedros_speech.txt", "r", encoding="utf-8") as file:
    tedros_transcript = file.read()

# Segment transcript into meaningful chunks
tedros_segments = [seg.strip() for seg in tedros_transcript.split("\n") if len(seg.strip()) > 30]

# Load sentiment analysis model (3-class)
sentiment_model_name = "cardiffnlp/twitter-roberta-base-sentiment"
sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)
sentiment_labels = ['negative', 'neutral', 'positive']

# Sentiment analysis function
def get_sentiment_scores(texts):
    scores = []
    for text in texts:
        inputs = sentiment_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = sentiment_model(**inputs).logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1).numpy()[0]
        sentiment = sentiment_labels[np.argmax(probabilities)]
        scores.append({
            "text": text,
            "negative": round(probabilities[0], 3),
            "neutral": round(probabilities[1], 3),
            "positive": round(probabilities[2], 3),
            "sentiment": sentiment
        })
    return pd.DataFrame(scores)

# Lexicon-based emotion function
def get_nrc_emotions(texts):
    import nltk  # Import nltk here

    # Download required NLTK data
    nltk.download('punkt_tab', quiet=True)  # Download punkt_tab data, suppress download messages
    nltk.download('punkt', quiet=True)      # Download punkt data, suppress download messages

    results = []
    for text in texts:
        emotion_obj = NRCLex(text)
        raw_scores = emotion_obj.raw_emotion_scores
        top_emotions = emotion_obj.top_emotions
        result = {
            "text": text,
            "raw_scores": raw_scores,
            "top_emotions": top_emotions
        }
        result.update(Counter(raw_scores))
        results.append(result)
    return pd.DataFrame(results)

# Run both analyses
tedros_sentiment_df = get_sentiment_scores(tedros_segments)
tedros_lexicon_df = get_nrc_emotions(tedros_segments)

# Merge dataframes on text segment
tedros_combined_df = pd.merge(tedros_sentiment_df, tedros_lexicon_df, on="text")

# Preview the combined data
tedros_combined_df.head()