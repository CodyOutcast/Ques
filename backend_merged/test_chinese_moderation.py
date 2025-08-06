"""
Test Tencent moderation with Mandarin Chinese characters
Tests both English and Chinese content across all moderation categories
"""
import asyncio
import sys
import os

# Add the backend path to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.enhanced_moderation import moderate_text_enhanced, moderate_image_enhanced, moderate_profile_enhanced

async def test_chinese_moderation():
    """Test moderation with Chinese characters"""
    
    print("🇨🇳 TESTING TENCENT MODERATION WITH CHINESE CHARACTERS")
    print("=" * 70)
    
    # Test cases in Chinese and English
    chinese_test_cases = [
        # Political content (应该被屏蔽)
        ("政治敏感", "习近平主席是我们的伟大领导人"),
        ("政治敏感", "共产党万岁，打倒资本主义"),
        ("政治敏感", "香港独立，台湾是独立国家"),
        ("政治敏感", "六四天安门事件真相"),
        
        # Drug content (毒品相关)
        ("毒品内容", "我卖大麻和可卡因，价格便宜"),
        ("毒品内容", "吸毒很爽，你要不要试试海洛因？"),
        ("毒品内容", "摇头丸和冰毒批发，微信联系"),
        ("毒品内容", "420friendly，大麻合法化"),
        
        # Sexual content (色情内容)
        ("色情内容", "今晚来我家做爱吧，我很饥渴"),
        ("色情内容", "想看我的裸照吗？发给我你的也"),
        ("色情内容", "一夜情，约炮，不要感情只要性"),
        ("色情内容", "我是性工作者，提供特殊服务"),
        
        # Terrorism/Violence (恐怖主义/暴力)
        ("恐怖主义", "我要制造炸弹攻击政府大楼"),
        ("恐怖主义", "杀死所有的异教徒，圣战万岁"),
        ("恐怖主义", "ISIS万岁，我要参加恐怖组织"),
        ("恐怖主义", "买枪买炸药，报复社会"),
        
        # Insults/Abuse (侮辱谩骂)
        ("侮辱谩骂", "你是个该死的白痴，去死吧"),
        ("侮辱谩骂", "傻逼东西，你全家都不得好死"),
        ("侮辱谩骂", "黑鬼滚回非洲，黄种人低等民族"),
        ("侮辱谩骂", "你妈是婊子，你爸是王八蛋"),
        
        # Advertising/Scam (广告诈骗)
        ("广告诈骗", "投资比特币，一夜暴富不是梦"),
        ("广告诈骗", "加微信领取免费iPhone，限时优惠"),
        ("广告诈骗", "网络兼职日赚千元，在家工作"),
        ("广告诈骗", "赌博网站推荐，注册送彩金"),
        
        # Illegal activities (违法活动)
        ("违法活动", "我可以帮你洗钱，手续费很低"),
        ("违法活动", "卖身份证和银行卡，价格面议"),
        ("违法活动", "代开发票，逃税避税服务"),
        ("违法活动", "人口贩卖，美女资源丰富"),
        
        # Normal content (正常内容 - 应该通过)
        ("正常内容", "你好，我是一名软件工程师"),
        ("正常内容", "我喜欢旅游和摄影，寻找志同道合的朋友"),
        ("正常内容", "今天天气真好，适合出去散步"),
        ("正常内容", "我在学习中文，希望能练习对话"),
    ]
    
    print("🔍 TESTING CHINESE TEXT MODERATION:")
    print("-" * 70)
    
    category_results = {}
    
    for category, text in chinese_test_cases:
        print(f"\n类别: {category}")
        print(f"文本: {text}")
        
        result = await moderate_text_enhanced(text, "chinese_test_user")
        
        status = "✅ 通过" if result.is_approved else "❌ 屏蔽"
        print(f"结果: {status}")
        print(f"置信度: {result.confidence:.2f}")
        print(f"模式: {result.mode}")
        
        if result.reason:
            print(f"原因: {result.reason}")
        
        if result.blocked_words:
            print(f"敏感词: {result.blocked_words}")
        
        if result.scores:
            high_scores = {k: v for k, v in result.scores.items() if v > 0}
            if high_scores:
                print(f"评分: {high_scores}")
        
        # Track results by category
        if category not in category_results:
            category_results[category] = {"blocked": 0, "total": 0}
        
        category_results[category]["total"] += 1
        if not result.is_approved:
            category_results[category]["blocked"] += 1
    
    # Mixed language test
    print(f"\n🔍 TESTING MIXED LANGUAGE CONTENT:")
    print("-" * 50)
    
    mixed_texts = [
        "Hello 你好, I want to sell drugs 我卖毒品",
        "Let's have sex 我们做爱吧 tonight",
        "Bitcoin investment 比特币投资 guaranteed profit",
        "你是 stupid idiot 白痴, go die 去死",
        "Normal conversation 正常对话 about weather 天气"
    ]
    
    for text in mixed_texts:
        result = await moderate_text_enhanced(text, "mixed_test")
        status = "✅ 通过" if result.is_approved else "❌ 屏蔽"
        print(f"'{text[:40]}...' → {status}")
        if result.reason:
            print(f"  原因: {result.reason}")
    
    # Category effectiveness summary
    print(f"\n📊 CATEGORY EFFECTIVENESS SUMMARY:")
    print("-" * 50)
    
    for category, stats in category_results.items():
        blocked = stats["blocked"]
        total = stats["total"]
        percentage = (blocked / total * 100) if total > 0 else 0
        effectiveness = "🔴 低效" if percentage < 50 else "🟡 中等" if percentage < 80 else "🟢 高效"
        
        print(f"{category}: {blocked}/{total} 屏蔽 ({percentage:.0f}%) {effectiveness}")
    
    # Test Chinese profile
    print(f"\n🔍 TESTING CHINESE PROFILE:")
    print("-" * 40)
    
    chinese_profile = {
        "bio": "我是性工作者，提供特殊服务。吸毒很爽，你要不要试试？",
        "occupation": "毒品销售员",
        "interests": "政治敏感话题，习近平主席",
        "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400"
    }
    
    profile_results = await moderate_profile_enhanced(chinese_profile, "chinese_profile_user")
    
    blocked_fields = []
    for field, result in profile_results.items():
        status = "✅ 通过" if result.is_approved else "❌ 屏蔽"
        print(f"{field}: {status} (置信度: {result.confidence:.2f})")
        
        if result.reason:
            print(f"  原因: {result.reason}")
        
        if not result.is_approved:
            blocked_fields.append(field)
    
    if blocked_fields:
        print(f"\n❌ 档案被屏蔽，原因: {', '.join(blocked_fields)}")
    else:
        print(f"\n✅ 档案通过审核")

if __name__ == "__main__":
    asyncio.run(test_chinese_moderation())
