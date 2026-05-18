from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider


def build_vietnamese_analyzer() -> AnalyzerEngine:
    cccd_recognizer = PatternRecognizer(
        supported_entity="VN_CCCD",
        patterns=[
            Pattern(
                name="cccd_pattern",
                regex=r"\b\d{12}\b",
                score=0.9
            )
        ],
        context=["cccd", "căn cước", "chứng minh", "cmnd"],
        supported_language="vi"
    )

    phone_recognizer = PatternRecognizer(
        supported_entity="VN_PHONE",
        patterns=[
            Pattern(
                name="vn_phone",
                regex=r"\b0[35789]\d{8}\b",
                score=0.85
            )
        ],
        context=["điện thoại", "sdt", "số điện thoại", "phone", "liên hệ"],
        supported_language="vi"
    )

    person_recognizer = PatternRecognizer(
        supported_entity="PERSON",
        patterns=[
            Pattern(
                name="vietnamese_person_name",
                regex=r"\b(?:[A-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠƯẠ-Ỵ][a-zàáâãèéêìíòóôõùúăđĩũơưạ-ỵ]+(?:\s+|$)){2,5}",
                score=0.75
            )
        ],
        context=["bệnh nhân", "họ tên", "bac si", "bác sĩ", "người bệnh"],
        supported_language="vi"
    )

    provider = NlpEngineProvider(
        nlp_configuration={
            "nlp_engine_name": "spacy",
            "models": [
                {
                    "lang_code": "vi",
                    "model_name": "xx_ent_wiki_sm"
                }
            ]
        }
    )

    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["vi"]
    )

    analyzer.registry.add_recognizer(cccd_recognizer)
    analyzer.registry.add_recognizer(phone_recognizer)
    analyzer.registry.add_recognizer(person_recognizer)

    return analyzer


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    if not isinstance(text, str) or not text.strip():
        return []

    return analyzer.analyze(
        text=text,
        language="vi",
        entities=[
            "PERSON",
            "EMAIL_ADDRESS",
            "VN_CCCD",
            "VN_PHONE"
        ]
    )