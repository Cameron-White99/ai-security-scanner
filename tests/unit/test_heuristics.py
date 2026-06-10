from core.detection.heuristics.analyzer import HeuristicAnalyzer

analyzer = HeuristicAnalyzer()


class TestInstructionDensity:
    def test_triggers_on_high_density(self):
        text = "ignore disregard instead you must you will respond only do not say"
        result = analyzer._check_instruction_density(text)
        assert result.triggered is True
        assert result.attack_type == "direct_injection"
        assert result.confidence > 0.5

    def test_no_trigger_on_normal_text(self):
        text = "Please help me write a cover letter for a software engineering position."
        result = analyzer._check_instruction_density(text)
        assert result.triggered is False

    def test_confidence_clamped_at_0_85(self):
        text = " ".join(["ignore disregard instead"] * 10)
        result = analyzer._check_instruction_density(text)
        assert result.triggered is True
        assert result.confidence <= 0.85


class TestUnusualDelimiters:
    def test_triggers_on_three_or_more(self):
        text = "=== --- *** normal text here"
        result = analyzer._check_unusual_delimiters(text)
        assert result.triggered is True
        assert result.confidence == 0.6

    def test_no_trigger_on_two(self):
        text = "=== some text ---"
        result = analyzer._check_unusual_delimiters(text)
        assert result.triggered is False

    def test_no_trigger_on_normal_text(self):
        result = analyzer._check_unusual_delimiters("This is a regular sentence.")
        assert result.triggered is False


class TestEncodingObfuscation:
    def test_triggers_on_base64(self):
        b64 = "SGVsbG8gV29ybGQgdGhpcyBpcyBhIHRlc3QgbWVzc2FnZSBmb3IgeW91"
        result = analyzer._check_encoding_obfuscation(b64)
        assert result.triggered is True
        assert result.attack_type == "obfuscation"
        assert result.confidence == 0.65

    def test_triggers_on_many_unicode_escapes(self):
        # 6 literal \uXXXX sequences (raw string) — len > 5 triggers the check
        text = "\\u0041\\u0042\\u0043\\u0044\\u0045\\u0046"
        result = analyzer._check_encoding_obfuscation(text)
        assert result.triggered is True

    def test_no_trigger_on_normal_text(self):
        result = analyzer._check_encoding_obfuscation("Hello world, how are you today?")
        assert result.triggered is False

    def test_no_trigger_on_few_unicode_escapes(self):
        # Only 3 — does not exceed threshold of 5
        text = "\\u0041\\u0042\\u0043"
        result = analyzer._check_encoding_obfuscation(text)
        assert result.triggered is False


class TestAnalyze:
    def test_returns_only_triggered_results(self):
        results = analyzer.analyze("Hello, can you help me with my homework?")
        assert all(r.triggered for r in results)

    def test_benign_text_returns_empty(self):
        results = analyzer.analyze("What is the capital of France?")
        assert results == []

    def test_injection_text_returns_results(self):
        text = "ignore disregard instead you must you will respond only"
        results = analyzer.analyze(text)
        assert len(results) > 0
