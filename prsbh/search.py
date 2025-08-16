#此文件由ai生成
import re

def search_mixed(items, search_term, threshold=50):
    def calculate_score(item, term):
        item_str = str(item).strip()
        term_str = str(term).strip()
        if item_str == term_str:
            return 100
        
        item_lower = item_str.lower()
        term_lower = term_str.lower()
        if term_lower in item_lower:
            score = 70 + (30 * min(1.0, len(term_str) / len(item_str)))
            return min(100, int(score))
        
        def split_tokens(text):
            tokens = []
            chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
            tokens.extend(chinese_chars)
            english_words = re.findall(r'[a-zA-Z]+', text)
            tokens.extend([w.lower() for w in english_words])
            return tokens
        
        item_tokens = split_tokens(item_str)
        term_tokens = split_tokens(term_str)
        
        if not term_tokens:
            return 0
            
        matched = 0
        total = len(term_tokens)
        
        for token in term_tokens:
            if token in item_tokens:
                matched += 1
            elif any(token in t for t in item_tokens if re.match(r'[a-zA-Z]', t)):
                matched += 0.5
                
        if matched > 0:
            return int(30 + (40 * (matched / total)))
        return 0
        
    matches = []
    for item in items:
        score = calculate_score(item, search_term)
        if score > threshold:
            matches.append((item, score))
    
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches