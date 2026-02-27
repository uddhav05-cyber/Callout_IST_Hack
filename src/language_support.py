"""
Language Support Module for Multilingual Verification

This module provides language detection, translation, and multilingual NLI support
for the fake news detection system.

Supported Languages:
- English (en)
- Spanish (es)
- French (fr)
- German (de)
- Hindi (hi)
- Chinese (zh)
- Arabic (ar)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
"""

import logging
from typing import Optional, Dict, List
from enum import Enum

logger = logging.getLogger(__name__)


class Language(str, Enum):
    """Supported languages for the system"""
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    HINDI = "hi"
    BENGALI = "bn"
    TAMIL = "ta"
    TELUGU = "te"
    MARATHI = "mr"
    GUJARATI = "gu"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    URDU = "ur"
    CHINESE = "zh"
    ARABIC = "ar"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    JAPANESE = "ja"
    AUTO = "auto"  # Auto-detect


# Language names for UI display
LANGUAGE_NAMES = {
    Language.ENGLISH: "English",
    Language.SPANISH: "Español",
    Language.FRENCH: "Français",
    Language.GERMAN: "Deutsch",
    Language.HINDI: "हिन्दी (Hindi)",
    Language.BENGALI: "বাংলা (Bengali)",
    Language.TAMIL: "தமிழ் (Tamil)",
    Language.TELUGU: "తెలుగు (Telugu)",
    Language.MARATHI: "मराठी (Marathi)",
    Language.GUJARATI: "ગુજરાતી (Gujarati)",
    Language.KANNADA: "ಕನ್ನಡ (Kannada)",
    Language.MALAYALAM: "മലയാളം (Malayalam)",
    Language.PUNJABI: "ਪੰਜਾਬੀ (Punjabi)",
    Language.URDU: "اردو (Urdu)",
    Language.CHINESE: "中文",
    Language.ARABIC: "العربية",
    Language.PORTUGUESE: "Português",
    Language.RUSSIAN: "Русский",
    Language.JAPANESE: "日本語",
    Language.AUTO: "Auto-detect"
}


# Multilingual NLI models
MULTILINGUAL_NLI_MODELS = {
    "default": "MoritzLaurer/mDeBERTa-v3-base-xnli-multilingual-nli-2mil7",
    "large": "joeddav/xlm-roberta-large-xnli",
    "fast": "facebook/bart-large-mnli"  # English only, but fast
}


def detectLanguage(text: str) -> Language:
    """
    Detect the language of the input text.
    
    Args:
        text: Text to detect language from
        
    Returns:
        Language enum value
        
    Note:
        Uses langdetect library. Falls back to English if detection fails.
    """
    if not text or len(text.strip()) < 10:
        logger.warning("Text too short for language detection, defaulting to English")
        return Language.ENGLISH
    
    try:
        from langdetect import detect, LangDetectException
        
        detected = detect(text)
        
        # Map langdetect codes to our Language enum
        language_map = {
            'en': Language.ENGLISH,
            'es': Language.SPANISH,
            'fr': Language.FRENCH,
            'de': Language.GERMAN,
            'hi': Language.HINDI,
            'bn': Language.BENGALI,
            'ta': Language.TAMIL,
            'te': Language.TELUGU,
            'mr': Language.MARATHI,
            'gu': Language.GUJARATI,
            'kn': Language.KANNADA,
            'ml': Language.MALAYALAM,
            'pa': Language.PUNJABI,
            'ur': Language.URDU,
            'zh-cn': Language.CHINESE,
            'zh-tw': Language.CHINESE,
            'ar': Language.ARABIC,
            'pt': Language.PORTUGUESE,
            'ru': Language.RUSSIAN,
            'ja': Language.JAPANESE
        }
        
        language = language_map.get(detected, Language.ENGLISH)
        logger.info(f"Detected language: {language.value} ({LANGUAGE_NAMES[language]})")
        return language
        
    except ImportError as e:
        logger.warning(f"langdetect library not installed: {e}. Defaulting to English")
        return Language.ENGLISH
    except Exception as e:
        logger.warning(f"Language detection failed: {e}. Defaulting to English")
        return Language.ENGLISH


def getMultilingualNLIModel(language: Language = Language.ENGLISH) -> str:
    """
    Get the appropriate NLI model for the given language.
    
    Args:
        language: Target language
        
    Returns:
        Model name/path for HuggingFace
    """
    # For English, use the fast BART model
    if language == Language.ENGLISH:
        return "facebook/bart-large-mnli"
    
    # For all other languages, use multilingual model
    return MULTILINGUAL_NLI_MODELS["default"]


def getClaimExtractionPrompt(language: Language) -> Dict[str, str]:
    """
    Get language-specific prompts for claim extraction.
    
    Args:
        language: Target language
        
    Returns:
        Dictionary with prompt templates
    """
    prompts = {
        Language.ENGLISH: {
            "system": "You are a fact-checking assistant. Extract atomic, verifiable factual claims from the article.",
            "instructions": """INSTRUCTIONS:
1. Extract ONLY factual claims that can be verified
2. DO NOT extract opinions, subjective statements, or predictions
3. Each claim should be atomic (one fact per claim) and self-contained
4. Assign an importance score (0.0 to 1.0) to each claim
5. Provide brief context for each claim

FORMAT YOUR RESPONSE AS:
CLAIM: [claim text]
IMPORTANCE: [score between 0.0 and 1.0]
CONTEXT: [brief context]
---"""
        },
        Language.SPANISH: {
            "system": "Eres un asistente de verificación de hechos. Extrae afirmaciones fácticas atómicas y verificables del artículo.",
            "instructions": """INSTRUCCIONES:
1. Extrae SOLO afirmaciones fácticas que puedan ser verificadas
2. NO extraigas opiniones, declaraciones subjetivas o predicciones
3. Cada afirmación debe ser atómica (un hecho por afirmación) y autónoma
4. Asigna una puntuación de importancia (0.0 a 1.0) a cada afirmación
5. Proporciona un contexto breve para cada afirmación

FORMATEA TU RESPUESTA COMO:
CLAIM: [texto de la afirmación]
IMPORTANCE: [puntuación entre 0.0 y 1.0]
CONTEXT: [contexto breve]
---"""
        },
        Language.FRENCH: {
            "system": "Vous êtes un assistant de vérification des faits. Extrayez des affirmations factuelles atomiques et vérifiables de l'article.",
            "instructions": """INSTRUCTIONS:
1. Extrayez UNIQUEMENT des affirmations factuelles vérifiables
2. N'extrayez PAS d'opinions, de déclarations subjectives ou de prédictions
3. Chaque affirmation doit être atomique (un fait par affirmation) et autonome
4. Attribuez un score d'importance (0.0 à 1.0) à chaque affirmation
5. Fournissez un contexte bref pour chaque affirmation

FORMATEZ VOTRE RÉPONSE COMME:
CLAIM: [texte de l'affirmation]
IMPORTANCE: [score entre 0.0 et 1.0]
CONTEXT: [contexte bref]
---"""
        },
        Language.GERMAN: {
            "system": "Sie sind ein Faktenprüfungsassistent. Extrahieren Sie atomare, überprüfbare faktische Behauptungen aus dem Artikel.",
            "instructions": """ANWEISUNGEN:
1. Extrahieren Sie NUR faktische Behauptungen, die überprüft werden können
2. Extrahieren Sie KEINE Meinungen, subjektive Aussagen oder Vorhersagen
3. Jede Behauptung sollte atomar (ein Fakt pro Behauptung) und eigenständig sein
4. Weisen Sie jeder Behauptung eine Wichtigkeitsbewertung (0.0 bis 1.0) zu
5. Geben Sie einen kurzen Kontext für jede Behauptung an

FORMATIEREN SIE IHRE ANTWORT WIE:
CLAIM: [Behauptungstext]
IMPORTANCE: [Bewertung zwischen 0.0 und 1.0]
CONTEXT: [kurzer Kontext]
---"""
        },
        Language.HINDI: {
            "system": "आप एक तथ्य-जांच सहायक हैं। लेख से परमाणु, सत्यापन योग्य तथ्यात्मक दावों को निकालें।",
            "instructions": """निर्देश:
1. केवल तथ्यात्मक दावों को निकालें जिन्हें सत्यापित किया जा सकता है
2. राय, व्यक्तिपरक बयान या भविष्यवाणियों को न निकालें
3. प्रत्येक दावा परमाणु (प्रति दावा एक तथ्य) और स्वतंत्र होना चाहिए
4. प्रत्येक दावे को महत्व स्कोर (0.0 से 1.0) दें
5. प्रत्येक दावे के लिए संक्षिप्त संदर्भ प्रदान करें

अपनी प्रतिक्रिया को इस प्रकार प्रारूपित करें:
CLAIM: [दावा पाठ]
IMPORTANCE: [0.0 और 1.0 के बीच स्कोर]
CONTEXT: [संक्षिप्त संदर्भ]
---"""
        },
        Language.CHINESE: {
            "system": "您是一个事实核查助手。从文章中提取原子的、可验证的事实声明。",
            "instructions": """说明：
1. 仅提取可以验证的事实声明
2. 不要提取意见、主观陈述或预测
3. 每个声明应该是原子的（每个声明一个事实）和独立的
4. 为每个声明分配重要性分数（0.0到1.0）
5. 为每个声明提供简要背景

按以下格式回复：
CLAIM: [声明文本]
IMPORTANCE: [0.0到1.0之间的分数]
CONTEXT: [简要背景]
---"""
        },
        Language.ARABIC: {
            "system": "أنت مساعد للتحقق من الحقائق. استخرج ادعاءات واقعية ذرية وقابلة للتحقق من المقال.",
            "instructions": """التعليمات:
1. استخرج فقط الادعاءات الواقعية التي يمكن التحقق منها
2. لا تستخرج الآراء أو البيانات الذاتية أو التنبؤات
3. يجب أن تكون كل ادعاء ذرية (حقيقة واحدة لكل ادعاء) ومستقلة
4. قم بتعيين درجة أهمية (0.0 إلى 1.0) لكل ادعاء
5. قدم سياقًا موجزًا لكل ادعاء

قم بتنسيق ردك كما يلي:
CLAIM: [نص الادعاء]
IMPORTANCE: [درجة بين 0.0 و 1.0]
CONTEXT: [سياق موجز]
---"""
        },
        Language.PORTUGUESE: {
            "system": "Você é um assistente de verificação de fatos. Extraia afirmações factuais atômicas e verificáveis do artigo.",
            "instructions": """INSTRUÇÕES:
1. Extraia APENAS afirmações factuais que possam ser verificadas
2. NÃO extraia opiniões, declarações subjetivas ou previsões
3. Cada afirmação deve ser atômica (um fato por afirmação) e autônoma
4. Atribua uma pontuação de importância (0.0 a 1.0) a cada afirmação
5. Forneça um contexto breve para cada afirmação

FORMATE SUA RESPOSTA COMO:
CLAIM: [texto da afirmação]
IMPORTANCE: [pontuação entre 0.0 e 1.0]
CONTEXT: [contexto breve]
---"""
        },
        Language.RUSSIAN: {
            "system": "Вы помощник по проверке фактов. Извлеките атомарные, проверяемые фактические утверждения из статьи.",
            "instructions": """ИНСТРУКЦИИ:
1. Извлекайте ТОЛЬКО фактические утверждения, которые можно проверить
2. НЕ извлекайте мнения, субъективные заявления или прогнозы
3. Каждое утверждение должно быть атомарным (один факт на утверждение) и самодостаточным
4. Присвойте оценку важности (от 0.0 до 1.0) каждому утверждению
5. Предоставьте краткий контекст для каждого утверждения

ФОРМАТИРУЙТЕ ОТВЕТ КАК:
CLAIM: [текст утверждения]
IMPORTANCE: [оценка от 0.0 до 1.0]
CONTEXT: [краткий контекст]
---"""
        },
        Language.JAPANESE: {
            "system": "あなたはファクトチェックアシスタントです。記事から原子的で検証可能な事実の主張を抽出してください。",
            "instructions": """指示：
1. 検証可能な事実の主張のみを抽出してください
2. 意見、主観的な発言、予測は抽出しないでください
3. 各主張は原子的（主張ごとに1つの事実）で自己完結している必要があります
4. 各主張に重要度スコア（0.0から1.0）を割り当ててください
5. 各主張に簡単な文脈を提供してください

次の形式で回答してください：
CLAIM: [主張のテキスト]
IMPORTANCE: [0.0から1.0の間のスコア]
CONTEXT: [簡単な文脈]
---"""
        },
        Language.BENGALI: {
            "system": "আপনি একজন তথ্য-যাচাই সহায়ক। নিবন্ধ থেকে পরমাণু, যাচাইযোগ্য তথ্যগত দাবি বের করুন।",
            "instructions": """নির্দেশাবলী:
1. শুধুমাত্র তথ্যগত দাবি বের করুন যা যাচাই করা যায়
2. মতামত, বিষয়ভিত্তিক বিবৃতি বা পূর্বাভাস বের করবেন না
3. প্রতিটি দাবি পরমাণু (প্রতি দাবিতে একটি তথ্য) এবং স্বয়ংসম্পূর্ণ হওয়া উচিত
4. প্রতিটি দাবিতে গুরুত্ব স্কোর (0.0 থেকে 1.0) বরাদ্দ করুন
5. প্রতিটি দাবির জন্য সংক্ষিপ্ত প্রসঙ্গ প্রদান করুন

আপনার প্রতিক্রিয়া এভাবে ফরম্যাট করুন:
CLAIM: [দাবির পাঠ্য]
IMPORTANCE: [0.0 এবং 1.0 এর মধ্যে স্কোর]
CONTEXT: [সংক্ষিপ্ত প্রসঙ্গ]
---"""
        },
        Language.TAMIL: {
            "system": "நீங்கள் ஒரு உண்மை சரிபார்ப்பு உதவியாளர். கட்டுரையிலிருந்து அணு, சரிபார்க்கக்கூடிய உண்மை கூற்றுகளை பிரித்தெடுக்கவும்.",
            "instructions": """வழிமுறைகள்:
1. சரிபார்க்கக்கூடிய உண்மை கூற்றுகளை மட்டும் பிரித்தெடுக்கவும்
2. கருத்துகள், அகநிலை அறிக்கைகள் அல்லது கணிப்புகளை பிரித்தெடுக்க வேண்டாம்
3. ஒவ்வொரு கூற்றும் அணுவாக (ஒரு கூற்றுக்கு ஒரு உண்மை) மற்றும் தன்னிறைவு பெற்றதாக இருக்க வேண்டும்
4. ஒவ்வொரு கூற்றுக்கும் முக்கியத்துவ மதிப்பெண் (0.0 முதல் 1.0 வரை) ஒதுக்கவும்
5. ஒவ்வொரு கூற்றுக்கும் சுருக்கமான சூழலை வழங்கவும்

உங்கள் பதிலை இவ்வாறு வடிவமைக்கவும்:
CLAIM: [கூற்று உரை]
IMPORTANCE: [0.0 மற்றும் 1.0 க்கு இடையிலான மதிப்பெண்]
CONTEXT: [சுருக்கமான சூழல்]
---"""
        },
        Language.TELUGU: {
            "system": "మీరు వాస్తవ-తనిఖీ సహాయకుడు. వ్యాసం నుండి పరమాణు, ధృవీకరించదగిన వాస్తవ వాదనలను సంగ్రహించండి.",
            "instructions": """సూచనలు:
1. ధృవీకరించదగిన వాస్తవ వాదనలను మాత్రమే సంగ్రహించండి
2. అభిప్రాయాలు, ఆత్మాశ్రయ ప్రకటనలు లేదా అంచనాలను సంగ్రహించవద్దు
3. ప్రతి వాదన పరమాణువుగా (ప్రతి వాదనకు ఒక వాస్తవం) మరియు స్వయం-నిర్వహణగా ఉండాలి
4. ప్రతి వాదనకు ప్రాముఖ్యత స్కోర్ (0.0 నుండి 1.0 వరకు) కేటాయించండి
5. ప్రతి వాదనకు సంక్షిప్త సందర్భాన్ని అందించండి

మీ ప్రతిస్పందనను ఈ విధంగా ఫార్మాట్ చేయండి:
CLAIM: [వాదన వచనం]
IMPORTANCE: [0.0 మరియు 1.0 మధ్య స్కోర్]
CONTEXT: [సంక్షిప్త సందర్భం]
---"""
        },
        Language.MARATHI: {
            "system": "तुम्ही तथ्य-तपासणी सहाय्यक आहात. लेखातून अणु, सत्यापित करण्यायोग्य वस्तुस्थितीचे दावे काढा.",
            "instructions": """सूचना:
1. फक्त वस्तुस्थितीचे दावे काढा जे सत्यापित केले जाऊ शकतात
2. मते, व्यक्तिनिष्ठ विधाने किंवा अंदाज काढू नका
3. प्रत्येक दावा अणु (प्रति दावा एक वस्तुस्थिती) आणि स्वयंपूर्ण असावा
4. प्रत्येक दाव्याला महत्त्व स्कोअर (0.0 ते 1.0) द्या
5. प्रत्येक दाव्यासाठी संक्षिप्त संदर्भ प्रदान करा

तुमचा प्रतिसाद अशा प्रकारे स्वरूपित करा:
CLAIM: [दावा मजकूर]
IMPORTANCE: [0.0 आणि 1.0 दरम्यान स्कोअर]
CONTEXT: [संक्षिप्त संदर्भ]
---"""
        },
        Language.GUJARATI: {
            "system": "તમે હકીકત-તપાસ સહાયક છો. લેખમાંથી અણુ, ચકાસી શકાય તેવા હકીકતલક્ષી દાવાઓ કાઢો.",
            "instructions": """સૂચનાઓ:
1. ફક્ત હકીકતલક્ષી દાવાઓ કાઢો જે ચકાસી શકાય
2. મંતવ્યો, વ્યક્તિલક્ષી નિવેદનો અથવા આગાહીઓ કાઢશો નહીં
3. દરેક દાવો અણુ (દાવા દીઠ એક હકીકત) અને સ્વયંપૂર્ણ હોવો જોઈએ
4. દરેક દાવાને મહત્વ સ્કોર (0.0 થી 1.0) સોંપો
5. દરેક દાવા માટે સંક્ષિપ્ત સંદર્ભ પ્રદાન કરો

તમારો પ્રતિસાદ આ રીતે ફોર્મેટ કરો:
CLAIM: [દાવો ટેક્સ્ટ]
IMPORTANCE: [0.0 અને 1.0 વચ્ચે સ્કોર]
CONTEXT: [સંક્ષિપ્ત સંદર્ભ]
---"""
        },
        Language.KANNADA: {
            "system": "ನೀವು ಸತ್ಯ-ಪರಿಶೀಲನೆ ಸಹಾಯಕರು. ಲೇಖನದಿಂದ ಪರಮಾಣು, ಪರಿಶೀಲಿಸಬಹುದಾದ ವಾಸ್ತವಿಕ ಹಕ್ಕುಗಳನ್ನು ಹೊರತೆಗೆಯಿರಿ.",
            "instructions": """ಸೂಚನೆಗಳು:
1. ಪರಿಶೀಲಿಸಬಹುದಾದ ವಾಸ್ತವಿಕ ಹಕ್ಕುಗಳನ್ನು ಮಾತ್ರ ಹೊರತೆಗೆಯಿರಿ
2. ಅಭಿಪ್ರಾಯಗಳು, ವ್ಯಕ್ತಿನಿಷ್ಠ ಹೇಳಿಕೆಗಳು ಅಥವಾ ಮುನ್ಸೂಚನೆಗಳನ್ನು ಹೊರತೆಗೆಯಬೇಡಿ
3. ಪ್ರತಿ ಹಕ್ಕು ಪರಮಾಣು (ಪ್ರತಿ ಹಕ್ಕಿಗೆ ಒಂದು ಸತ್ಯ) ಮತ್ತು ಸ್ವಯಂ-ಒಳಗೊಂಡಿರಬೇಕು
4. ಪ್ರತಿ ಹಕ್ಕಿಗೆ ಪ್ರಾಮುಖ್ಯತೆ ಸ್ಕೋರ್ (0.0 ರಿಂದ 1.0) ನಿಯೋಜಿಸಿ
5. ಪ್ರತಿ ಹಕ್ಕಿಗೆ ಸಂಕ್ಷಿಪ್ತ ಸಂದರ್ಭವನ್ನು ಒದಗಿಸಿ

ನಿಮ್ಮ ಪ್ರತಿಕ್ರಿಯೆಯನ್ನು ಈ ರೀತಿ ಫಾರ್ಮ್ಯಾಟ್ ಮಾಡಿ:
CLAIM: [ಹಕ್ಕು ಪಠ್ಯ]
IMPORTANCE: [0.0 ಮತ್ತು 1.0 ನಡುವಿನ ಸ್ಕೋರ್]
CONTEXT: [ಸಂಕ್ಷಿಪ್ತ ಸಂದರ್ಭ]
---"""
        },
        Language.MALAYALAM: {
            "system": "നിങ്ങൾ ഒരു വസ്തുത-പരിശോധന സഹായകനാണ്. ലേഖനത്തിൽ നിന്ന് ആറ്റോമിക്, പരിശോധിക്കാവുന്ന വസ്തുതാപരമായ അവകാശവാദങ്ങൾ എക്സ്ട്രാക്റ്റ് ചെയ്യുക.",
            "instructions": """നിർദ്ദേശങ്ങൾ:
1. പരിശോധിക്കാവുന്ന വസ്തുതാപരമായ അവകാശവാദങ്ങൾ മാത്രം എക്സ്ട്രാക്റ്റ് ചെയ്യുക
2. അഭിപ്രായങ്ങൾ, ആത്മനിഷ്ഠ പ്രസ്താവനകൾ അല്ലെങ്കിൽ പ്രവചനങ്ങൾ എക്സ്ട്രാക്റ്റ് ചെയ്യരുത്
3. ഓരോ അവകാശവാദവും ആറ്റോമിക് (ഓരോ അവകാശവാദത്തിനും ഒരു വസ്തുത) ആയിരിക്കണം
4. ഓരോ അവകാശവാദത്തിനും പ്രാധാന്യ സ്കോർ (0.0 മുതൽ 1.0 വരെ) നൽകുക
5. ഓരോ അവകാശവാദത്തിനും ഹ്രസ്വ സന്ദർഭം നൽകുക

നിങ്ങളുടെ പ്രതികരണം ഇങ്ങനെ ഫോർമാറ്റ് ചെയ്യുക:
CLAIM: [അവകാശവാദ വാചകം]
IMPORTANCE: [0.0 നും 1.0 നും ഇടയിലുള്ള സ്കോർ]
CONTEXT: [ഹ്രസ്വ സന്ദർഭം]
---"""
        },
        Language.PUNJABI: {
            "system": "ਤੁਸੀਂ ਇੱਕ ਤੱਥ-ਜਾਂਚ ਸਹਾਇਕ ਹੋ। ਲੇਖ ਤੋਂ ਪਰਮਾਣੂ, ਪ੍ਰਮਾਣਿਤ ਕੀਤੇ ਜਾ ਸਕਣ ਵਾਲੇ ਤੱਥਾਤਮਕ ਦਾਅਵੇ ਕੱਢੋ।",
            "instructions": """ਨਿਰਦੇਸ਼:
1. ਸਿਰਫ਼ ਤੱਥਾਤਮਕ ਦਾਅਵੇ ਕੱਢੋ ਜੋ ਪ੍ਰਮਾਣਿਤ ਕੀਤੇ ਜਾ ਸਕਦੇ ਹਨ
2. ਰਾਏ, ਵਿਅਕਤੀਗਤ ਬਿਆਨ ਜਾਂ ਭਵਿੱਖਬਾਣੀਆਂ ਨੂੰ ਨਾ ਕੱਢੋ
3. ਹਰੇਕ ਦਾਅਵਾ ਪਰਮਾਣੂ (ਪ੍ਰਤੀ ਦਾਅਵੇ ਇੱਕ ਤੱਥ) ਅਤੇ ਸਵੈ-ਨਿਰਭਰ ਹੋਣਾ ਚਾਹੀਦਾ ਹੈ
4. ਹਰੇਕ ਦਾਅਵੇ ਨੂੰ ਮਹੱਤਵ ਸਕੋਰ (0.0 ਤੋਂ 1.0) ਦਿਓ
5. ਹਰੇਕ ਦਾਅਵੇ ਲਈ ਸੰਖੇਪ ਸੰਦਰਭ ਪ੍ਰਦਾਨ ਕਰੋ

ਆਪਣੇ ਜਵਾਬ ਨੂੰ ਇਸ ਤਰ੍ਹਾਂ ਫਾਰਮੈਟ ਕਰੋ:
CLAIM: [ਦਾਅਵਾ ਟੈਕਸਟ]
IMPORTANCE: [0.0 ਅਤੇ 1.0 ਵਿਚਕਾਰ ਸਕੋਰ]
CONTEXT: [ਸੰਖੇਪ ਸੰਦਰਭ]
---"""
        },
        Language.URDU: {
            "system": "آپ ایک حقیقت کی تصدیق کرنے والے معاون ہیں۔ مضمون سے جوہری، قابل تصدیق حقائق پر مبنی دعوے نکالیں۔",
            "instructions": """ہدایات:
1. صرف حقائق پر مبنی دعوے نکالیں جن کی تصدیق کی جا سکتی ہے
2. رائے، ذاتی بیانات یا پیشین گوئیاں نہ نکالیں
3. ہر دعویٰ جوہری (فی دعویٰ ایک حقیقت) اور خود مکتفی ہونا چاہیے
4. ہر دعوے کو اہمیت کا سکور (0.0 سے 1.0) تفویض کریں
5. ہر دعوے کے لیے مختصر سیاق و سباق فراہم کریں

اپنے جواب کو اس طرح فارمیٹ کریں:
CLAIM: [دعوے کا متن]
IMPORTANCE: [0.0 اور 1.0 کے درمیان سکور]
CONTEXT: [مختصر سیاق و سباق]
---"""
        }
    }
    
    return prompts.get(language, prompts[Language.ENGLISH])


def getUITranslations(language: Language) -> Dict[str, str]:
    """
    Get UI translations for the given language.
    
    Args:
        language: Target language
        
    Returns:
        Dictionary with UI text translations
    """
    translations = {
        Language.ENGLISH: {
            "app_title": "Callout - Fake News Detector",
            "app_subtitle": "AI-powered misinformation detection using Natural Language Inference",
            "analyze_button": "Analyze Article",
            "url_input_label": "Article URL",
            "text_input_label": "Article Text",
            "language_selector": "Select Language",
            "overall_verdict": "Overall Verdict",
            "confidence_score": "Confidence Score",
            "factual_accuracy": "Factual Accuracy",
            "emotional_manipulation": "Emotional Manipulation",
            "claims_analyzed": "Claims Analyzed",
            "evidence_sources": "Evidence Sources",
            "verified_claims": "Verified Claims",
            "explanation": "Explanation",
            "claim_breakdown": "Claim-by-Claim Analysis",
            "evidence_cards": "Evidence Cards",
            "export_results": "Export & Share Results",
            "analyzing": "Analysis in Progress",
            "stage_1": "Parsing article content...",
            "stage_2": "Extracting factual claims from article...",
            "stage_3": "Retrieving evidence from credible sources...",
            "stage_4": "Verifying claims using AI (NLI)...",
            "stage_5": "Analyzing tone and synthesizing final verdict...",
            "analysis_complete": "Analysis complete!",
            "verdict_true": "Claims are supported by evidence",
            "verdict_false": "Claims are contradicted by evidence",
            "verdict_misleading": "Mixed or partial truth",
            "verdict_unverified": "Insufficient evidence"
        },
        Language.SPANISH: {
            "app_title": "Callout - Detector de Noticias Falsas",
            "app_subtitle": "Detección de desinformación impulsada por IA usando Inferencia de Lenguaje Natural",
            "analyze_button": "Analizar Artículo",
            "url_input_label": "URL del Artículo",
            "text_input_label": "Texto del Artículo",
            "language_selector": "Seleccionar Idioma",
            "overall_verdict": "Veredicto General",
            "confidence_score": "Puntuación de Confianza",
            "factual_accuracy": "Precisión Factual",
            "emotional_manipulation": "Manipulación Emocional",
            "claims_analyzed": "Afirmaciones Analizadas",
            "evidence_sources": "Fuentes de Evidencia",
            "verified_claims": "Afirmaciones Verificadas",
            "explanation": "Explicación",
            "claim_breakdown": "Análisis Afirmación por Afirmación",
            "evidence_cards": "Tarjetas de Evidencia",
            "export_results": "Exportar y Compartir Resultados",
            "analyzing": "Análisis en Progreso",
            "stage_1": "Analizando contenido del artículo...",
            "stage_2": "Extrayendo afirmaciones factuales del artículo...",
            "stage_3": "Recuperando evidencia de fuentes creíbles...",
            "stage_4": "Verificando afirmaciones usando IA (NLI)...",
            "stage_5": "Analizando tono y sintetizando veredicto final...",
            "analysis_complete": "¡Análisis completo!",
            "verdict_true": "Las afirmaciones están respaldadas por evidencia",
            "verdict_false": "Las afirmaciones son contradichas por evidencia",
            "verdict_misleading": "Verdad mixta o parcial",
            "verdict_unverified": "Evidencia insuficiente"
        },
        Language.FRENCH: {
            "app_title": "Callout - Détecteur de Fausses Nouvelles",
            "app_subtitle": "Détection de désinformation alimentée par l'IA utilisant l'Inférence de Langage Naturel",
            "analyze_button": "Analyser l'Article",
            "url_input_label": "URL de l'Article",
            "text_input_label": "Texte de l'Article",
            "language_selector": "Sélectionner la Langue",
            "overall_verdict": "Verdict Global",
            "confidence_score": "Score de Confiance",
            "factual_accuracy": "Précision Factuelle",
            "emotional_manipulation": "Manipulation Émotionnelle",
            "claims_analyzed": "Affirmations Analysées",
            "evidence_sources": "Sources de Preuves",
            "verified_claims": "Affirmations Vérifiées",
            "explanation": "Explication",
            "claim_breakdown": "Analyse Affirmation par Affirmation",
            "evidence_cards": "Cartes de Preuves",
            "export_results": "Exporter et Partager les Résultats",
            "analyzing": "Analyse en Cours",
            "stage_1": "Analyse du contenu de l'article...",
            "stage_2": "Extraction des affirmations factuelles de l'article...",
            "stage_3": "Récupération de preuves de sources crédibles...",
            "stage_4": "Vérification des affirmations à l'aide de l'IA (NLI)...",
            "stage_5": "Analyse du ton et synthèse du verdict final...",
            "analysis_complete": "Analyse terminée!",
            "verdict_true": "Les affirmations sont soutenues par des preuves",
            "verdict_false": "Les affirmations sont contredites par des preuves",
            "verdict_misleading": "Vérité mixte ou partielle",
            "verdict_unverified": "Preuves insuffisantes"
        },
        Language.HINDI: {
            "app_title": "Callout - फेक न्यूज डिटेक्टर",
            "app_subtitle": "प्राकृतिक भाषा अनुमान का उपयोग करके AI-संचालित गलत सूचना का पता लगाना",
            "analyze_button": "लेख का विश्लेषण करें",
            "url_input_label": "लेख URL",
            "text_input_label": "लेख पाठ",
            "language_selector": "भाषा चुनें",
            "overall_verdict": "समग्र निर्णय",
            "confidence_score": "विश्वास स्कोर",
            "factual_accuracy": "तथ्यात्मक सटीकता",
            "emotional_manipulation": "भावनात्मक हेरफेर",
            "claims_analyzed": "विश्लेषित दावे",
            "evidence_sources": "साक्ष्य स्रोत",
            "verified_claims": "सत्यापित दावे",
            "explanation": "व्याख्या",
            "claim_breakdown": "दावा-दर-दावा विश्लेषण",
            "evidence_cards": "साक्ष्य कार्ड",
            "export_results": "परिणाम निर्यात और साझा करें",
            "analyzing": "विश्लेषण प्रगति में",
            "stage_1": "लेख सामग्री का विश्लेषण...",
            "stage_2": "लेख से तथ्यात्मक दावों को निकालना...",
            "stage_3": "विश्वसनीय स्रोतों से साक्ष्य प्राप्त करना...",
            "stage_4": "AI (NLI) का उपयोग करके दावों को सत्यापित करना...",
            "stage_5": "स्वर का विश्लेषण और अंतिम निर्णय संश्लेषण...",
            "analysis_complete": "विश्लेषण पूर्ण!",
            "verdict_true": "दावे साक्ष्य द्वारा समर्थित हैं",
            "verdict_false": "दावे साक्ष्य द्वारा खंडित हैं",
            "verdict_misleading": "मिश्रित या आंशिक सत्य",
            "verdict_unverified": "अपर्याप्त साक्ष्य"
        },
        Language.CHINESE: {
            "app_title": "Callout - 假新闻检测器",
            "app_subtitle": "使用自然语言推理的AI驱动的错误信息检测",
            "analyze_button": "分析文章",
            "url_input_label": "文章URL",
            "text_input_label": "文章文本",
            "language_selector": "选择语言",
            "overall_verdict": "总体判决",
            "confidence_score": "置信度分数",
            "factual_accuracy": "事实准确性",
            "emotional_manipulation": "情感操纵",
            "claims_analyzed": "已分析声明",
            "evidence_sources": "证据来源",
            "verified_claims": "已验证声明",
            "explanation": "解释",
            "claim_breakdown": "逐项声明分析",
            "evidence_cards": "证据卡",
            "export_results": "导出和分享结果",
            "analyzing": "分析进行中",
            "stage_1": "解析文章内容...",
            "stage_2": "从文章中提取事实声明...",
            "stage_3": "从可信来源检索证据...",
            "stage_4": "使用AI（NLI）验证声明...",
            "stage_5": "分析语气并综合最终判决...",
            "analysis_complete": "分析完成！",
            "verdict_true": "声明得到证据支持",
            "verdict_false": "声明被证据反驳",
            "verdict_misleading": "混合或部分真相",
            "verdict_unverified": "证据不足"
        },
        Language.BENGALI: {
            "app_title": "Callout - ভুয়া খবর সনাক্তকারী",
            "app_subtitle": "প্রাকৃতিক ভাষা অনুমান ব্যবহার করে AI-চালিত ভুল তথ্য সনাক্তকরণ",
            "analyze_button": "নিবন্ধ বিশ্লেষণ করুন",
            "url_input_label": "নিবন্ধ URL",
            "text_input_label": "নিবন্ধ পাঠ্য",
            "language_selector": "ভাষা নির্বাচন করুন",
            "overall_verdict": "সামগ্রিক রায়",
            "confidence_score": "আত্মবিশ্বাস স্কোর",
            "factual_accuracy": "তথ্যগত নির্ভুলতা",
            "emotional_manipulation": "আবেগজনক কারসাজি",
            "claims_analyzed": "বিশ্লেষিত দাবি",
            "evidence_sources": "প্রমাণ উৎস",
            "verified_claims": "যাচাইকৃত দাবি",
            "explanation": "ব্যাখ্যা",
            "claim_breakdown": "দাবি-দর-দাবি বিশ্লেষণ",
            "evidence_cards": "প্রমাণ কার্ড",
            "export_results": "ফলাফল রপ্তানি এবং শেয়ার করুন",
            "analyzing": "বিশ্লেষণ চলছে",
            "stage_1": "নিবন্ধ বিষয়বস্তু পার্স করা হচ্ছে...",
            "stage_2": "নিবন্ধ থেকে তথ্যগত দাবি বের করা হচ্ছে...",
            "stage_3": "বিশ্বস্ত উৎস থেকে প্রমাণ পুনরুদ্ধার করা হচ্ছে...",
            "stage_4": "AI (NLI) ব্যবহার করে দাবি যাচাই করা হচ্ছে...",
            "stage_5": "স্বর বিশ্লেষণ এবং চূড়ান্ত রায় সংশ্লেষণ...",
            "analysis_complete": "বিশ্লেষণ সম্পূর্ণ!",
            "verdict_true": "দাবিগুলি প্রমাণ দ্বারা সমর্থিত",
            "verdict_false": "দাবিগুলি প্রমাণ দ্বারা খণ্ডিত",
            "verdict_misleading": "মিশ্র বা আংশিক সত্য",
            "verdict_unverified": "অপর্যাপ্ত প্রমাণ"
        },
        Language.TAMIL: {
            "app_title": "Callout - போலி செய்தி கண்டறிதல்",
            "app_subtitle": "இயற்கை மொழி அனுமானத்தைப் பயன்படுத்தி AI-இயக்கப்படும் தவறான தகவல் கண்டறிதல்",
            "analyze_button": "கட்டுரையை பகுப்பாய்வு செய்யவும்",
            "url_input_label": "கட்டுரை URL",
            "text_input_label": "கட்டுரை உரை",
            "language_selector": "மொழியைத் தேர்ந்தெடுக்கவும்",
            "overall_verdict": "ஒட்டுமொத்த தீர்ப்பு",
            "confidence_score": "நம்பிக்கை மதிப்பெண்",
            "factual_accuracy": "உண்மை துல்லியம்",
            "emotional_manipulation": "உணர்ச்சி கையாளுதல்",
            "claims_analyzed": "பகுப்பாய்வு செய்யப்பட்ட கூற்றுகள்",
            "evidence_sources": "சான்று ஆதாரங்கள்",
            "verified_claims": "சரிபார்க்கப்பட்ட கூற்றுகள்",
            "explanation": "விளக்கம்",
            "claim_breakdown": "கூற்று-வாரியான பகுப்பாய்வு",
            "evidence_cards": "சான்று அட்டைகள்",
            "export_results": "முடிவுகளை ஏற்றுமதி மற்றும் பகிரவும்",
            "analyzing": "பகுப்பாய்வு நடந்து கொண்டிருக்கிறது",
            "stage_1": "கட்டுரை உள்ளடக்கத்தை பகுப்பாய்வு செய்கிறது...",
            "stage_2": "கட்டுரையிலிருந்து உண்மை கூற்றுகளை பிரித்தெடுக்கிறது...",
            "stage_3": "நம்பகமான ஆதாரங்களிலிருந்து சான்றுகளை மீட்டெடுக்கிறது...",
            "stage_4": "AI (NLI) பயன்படுத்தி கூற்றுகளை சரிபார்க்கிறது...",
            "stage_5": "தொனியை பகுப்பாய்வு செய்து இறுதி தீர்ப்பை தொகுக்கிறது...",
            "analysis_complete": "பகுப்பாய்வு முடிந்தது!",
            "verdict_true": "கூற்றுகள் சான்றுகளால் ஆதரிக்கப்படுகின்றன",
            "verdict_false": "கூற்றுகள் சான்றுகளால் மறுக்கப்படுகின்றன",
            "verdict_misleading": "கலப்பு அல்லது பகுதி உண்மை",
            "verdict_unverified": "போதிய சான்றுகள் இல்லை"
        },
        Language.TELUGU: {
            "app_title": "Callout - నకిలీ వార్తల గుర్తింపు",
            "app_subtitle": "సహజ భాష అనుమానాన్ని ఉపయోగించి AI-ఆధారిత తప్పుడు సమాచార గుర్తింపు",
            "analyze_button": "వ్యాసాన్ని విశ్లేషించండి",
            "url_input_label": "వ్యాస URL",
            "text_input_label": "వ్యాస వచనం",
            "language_selector": "భాషను ఎంచుకోండి",
            "overall_verdict": "మొత్తం తీర్పు",
            "confidence_score": "విశ్వాస స్కోర్",
            "factual_accuracy": "వాస్తవ ఖచ్చితత్వం",
            "emotional_manipulation": "భావోద్వేగ తారుమారు",
            "claims_analyzed": "విశ్లేషించిన వాదనలు",
            "evidence_sources": "సాక్ష్యం మూలాలు",
            "verified_claims": "ధృవీకరించిన వాదనలు",
            "explanation": "వివరణ",
            "claim_breakdown": "వాదన-వారీ విశ్లేషణ",
            "evidence_cards": "సాక్ష్యం కార్డులు",
            "export_results": "ఫలితాలను ఎగుమతి మరియు భాగస్వామ్యం చేయండి",
            "analyzing": "విశ్లేషణ జరుగుతోంది",
            "stage_1": "వ్యాస కంటెంట్‌ను పార్స్ చేస్తోంది...",
            "stage_2": "వ్యాసం నుండి వాస్తవ వాదనలను సంగ్రహిస్తోంది...",
            "stage_3": "విశ్వసనీయ మూలాల నుండి సాక్ష్యాలను తిరిగి పొందుతోంది...",
            "stage_4": "AI (NLI) ఉపయోగించి వాదనలను ధృవీకరిస్తోంది...",
            "stage_5": "టోన్‌ను విశ్లేషిస్తోంది మరియు చివరి తీర్పును సంశ్లేషిస్తోంది...",
            "analysis_complete": "విశ్లేషణ పూర్తయింది!",
            "verdict_true": "వాదనలు సాక్ష్యం ద్వారా మద్దతు ఇవ్వబడ్డాయి",
            "verdict_false": "వాదనలు సాక్ష్యం ద్వారా ఖండించబడ్డాయి",
            "verdict_misleading": "మిశ్రమ లేదా పాక్షిక సత్యం",
            "verdict_unverified": "తగినంత సాక్ష్యం లేదు"
        },
        Language.MARATHI: {
            "app_title": "Callout - खोटी बातमी शोधक",
            "app_subtitle": "नैसर्गिक भाषा अनुमान वापरून AI-चालित चुकीची माहिती शोध",
            "analyze_button": "लेखाचे विश्लेषण करा",
            "url_input_label": "लेख URL",
            "text_input_label": "लेख मजकूर",
            "language_selector": "भाषा निवडा",
            "overall_verdict": "एकूण निर्णय",
            "confidence_score": "आत्मविश्वास स्कोअर",
            "factual_accuracy": "वस्तुस्थितीची अचूकता",
            "emotional_manipulation": "भावनिक हेराफेरी",
            "claims_analyzed": "विश्लेषित दावे",
            "evidence_sources": "पुरावा स्रोत",
            "verified_claims": "सत्यापित दावे",
            "explanation": "स्पष्टीकरण",
            "claim_breakdown": "दावा-दर-दावा विश्लेषण",
            "evidence_cards": "पुरावा कार्डे",
            "export_results": "परिणाम निर्यात आणि सामायिक करा",
            "analyzing": "विश्लेषण सुरू आहे",
            "stage_1": "लेख सामग्री पार्स करत आहे...",
            "stage_2": "लेखातून वस्तुस्थितीचे दावे काढत आहे...",
            "stage_3": "विश्वासार्ह स्रोतांकडून पुरावा पुनर्प्राप्त करत आहे...",
            "stage_4": "AI (NLI) वापरून दावे सत्यापित करत आहे...",
            "stage_5": "स्वर विश्लेषण आणि अंतिम निर्णय संश्लेषण...",
            "analysis_complete": "विश्लेषण पूर्ण!",
            "verdict_true": "दावे पुराव्याद्वारे समर्थित आहेत",
            "verdict_false": "दावे पुराव्याद्वारे खंडित केले आहेत",
            "verdict_misleading": "मिश्र किंवा आंशिक सत्य",
            "verdict_unverified": "अपुरा पुरावा"
        }
    }
    
    return translations.get(language, translations[Language.ENGLISH])


def translateVerdict(verdict: str, language: Language) -> str:
    """
    Translate verdict type to target language.
    
    Args:
        verdict: Verdict type (LIKELY_TRUE, LIKELY_FALSE, etc.)
        language: Target language
        
    Returns:
        Translated verdict string
    """
    verdict_translations = {
        Language.ENGLISH: {
            "LIKELY_TRUE": "LIKELY TRUE",
            "LIKELY_FALSE": "LIKELY FALSE",
            "MISLEADING": "MISLEADING",
            "UNVERIFIED": "UNVERIFIED",
            "TRUE": "TRUE",
            "FALSE": "FALSE"
        },
        Language.SPANISH: {
            "LIKELY_TRUE": "PROBABLEMENTE VERDADERO",
            "LIKELY_FALSE": "PROBABLEMENTE FALSO",
            "MISLEADING": "ENGAÑOSO",
            "UNVERIFIED": "NO VERIFICADO",
            "TRUE": "VERDADERO",
            "FALSE": "FALSO"
        },
        Language.FRENCH: {
            "LIKELY_TRUE": "PROBABLEMENT VRAI",
            "LIKELY_FALSE": "PROBABLEMENT FAUX",
            "MISLEADING": "TROMPEUR",
            "UNVERIFIED": "NON VÉRIFIÉ",
            "TRUE": "VRAI",
            "FALSE": "FAUX"
        },
        Language.HINDI: {
            "LIKELY_TRUE": "संभवतः सत्य",
            "LIKELY_FALSE": "संभवतः असत्य",
            "MISLEADING": "भ्रामक",
            "UNVERIFIED": "असत्यापित",
            "TRUE": "सत्य",
            "FALSE": "असत्य"
        },
        Language.CHINESE: {
            "LIKELY_TRUE": "可能真实",
            "LIKELY_FALSE": "可能虚假",
            "MISLEADING": "误导性",
            "UNVERIFIED": "未经验证",
            "TRUE": "真实",
            "FALSE": "虚假"
        }
    }
    
    translations = verdict_translations.get(language, verdict_translations[Language.ENGLISH])
    return translations.get(verdict, verdict)


__all__ = [
    'Language',
    'LANGUAGE_NAMES',
    'MULTILINGUAL_NLI_MODELS',
    'detectLanguage',
    'getMultilingualNLIModel',
    'getClaimExtractionPrompt',
    'getUITranslations',
    'translateVerdict'
]
