#!/usr/bin/env python3
"""
智能搜索代理集成测试
测试基于真实users_rawjson集合的完整搜索流程和新增的智能交互功能
包括意图识别、询问处理、聊天处理等新功能
"""

import asyncio
import sys
import os
import random
from typing import Dict, List

# 加载环境变量
from dotenv import load_dotenv
load_dotenv()

# 添加src路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from vector_search.intelligent_search_agent import create_search_agent
from vector_search.config import Config
from qdrant_client import QdrantClient


class IntegrationTestSuite:
    def __init__(self):
        self.config = Config()
        self.qdrant_client = QdrantClient(
            host=self.config.qdrant_host,
            port=self.config.qdrant_port
        )
        # 创建搜索代理实例
        self.search_agent = create_search_agent(
            glm_api_key=self.config.glm_api_key,
            qdrant_client=self.qdrant_client
        )
        self.test_results = []
    
    def get_random_user_id(self) -> str:
        """获取1-550范围内的随机用户ID"""
        return str(random.randint(1, 550))
    
    # ===== 新功能测试方法 =====
    
    async def test_intent_analysis(self):
        """测试意图识别功能"""
        print(f"\n{'='*60}")
        print("新功能测试 1: 意图识别系统")
        print(f"{'='*60}")
        
        test_cases = [
            {
                "input": "帮我找一个会Python的工程师",
                "expected": "search",
                "description": "搜索意图 - 寻找技能"
            },
            {
                "input": "这个人的技能怎么样？",
                "expected": "inquiry",
                "description": "询问意图 - 询问用户信息",
                "referenced_user": {"name": "张三", "skills": ["Python", "Java"]}
            },
            {
                "input": "你好",
                "expected": "chat",
                "description": "聊天意图 - 问候"
            },
            {
                "input": "寻找在北京的AI算法工程师",
                "expected": "search",
                "description": "搜索意图 - 地理位置+技能"
            },
            {
                "input": "他适合我们的项目吗？",
                "expected": "inquiry",
                "description": "询问意图 - 适配性分析",
                "referenced_user": {"name": "李四", "skills": ["AI", "ML"]}
            },
            {
                "input": "这个系统怎么用？",
                "expected": "chat",
                "description": "聊天意图 - 咨询"
            }
        ]
        
        intent_results = {
            "correct": 0,
            "total": len(test_cases),
            "details": []
        }
        
        for i, case in enumerate(test_cases, 1):
            try:
                print(f"\n测试案例 {i}: {case['description']}")
                print(f"  输入: '{case['input']}'")
                
                referenced_user = case.get("referenced_user")
                
                result = self.search_agent.analyze_user_intent(
                    user_input=case["input"],
                    referenced_user=referenced_user
                )
                
                intent = result.get("intent")
                confidence = result.get("confidence", 0)
                reasoning = result.get("reasoning", "")
                
                print(f"  识别意图: {intent} (置信度: {confidence:.2f})")
                print(f"  预期意图: {case['expected']}")
                print(f"  推理过程: {reasoning[:100]}...")
                
                is_correct = intent == case["expected"]
                if is_correct:
                    intent_results["correct"] += 1
                    print("  ✅ 意图识别正确")
                else:
                    print("  ⚠️ 意图识别不准确")
                
                intent_results["details"].append({
                    "case": case["description"],
                    "input": case["input"],
                    "expected": case["expected"],
                    "actual": intent,
                    "confidence": confidence,
                    "correct": is_correct
                })
                
            except Exception as e:
                print(f"  ❌ 测试失败: {e}")
                intent_results["details"].append({
                    "case": case["description"],
                    "error": str(e),
                    "correct": False
                })
        
        accuracy = intent_results["correct"] / intent_results["total"] * 100
        print(f"\n🎯 意图识别准确率: {accuracy:.1f}% ({intent_results['correct']}/{intent_results['total']})")
        
        return intent_results
    
    async def test_intelligent_conversation(self):
        """测试智能交互统一入口"""
        print(f"\n{'='*60}")
        print("新功能测试 2: 智能交互统一入口")
        print(f"{'='*60}")
        
        # 获取两个随机用户ID用于测试
        current_user_id = self.get_random_user_id()
        referenced_user_id = self.get_random_user_id()
        
        test_cases = [
            {
                "name": "搜索模式测试",
                "input": "帮我找一个Python开发工程师",
                "user_id": current_user_id,
                "expected_type": "search"
            },
            {
                "name": "询问模式测试",
                "input": "这个人的背景怎么样？",
                "user_id": current_user_id,
                "referenced_ids": [referenced_user_id],
                "expected_type": "inquiry"
            },
            {
                "name": "聊天模式测试",
                "input": "你好，请介绍一下这个系统",
                "user_id": current_user_id,
                "expected_type": "chat"
            }
        ]
        
        conversation_results = {
            "success": 0,
            "total": len(test_cases),
            "details": []
        }
        
        for i, case in enumerate(test_cases, 1):
            try:
                print(f"\n测试案例 {i}: {case['name']}")
                print(f"  输入: '{case['input']}'")
                print(f"  用户ID: {case.get('user_id', 'None')}")
                print(f"  引用用户: {case.get('referenced_ids', 'None')}")
                
                result = await self.search_agent.intelligent_conversation(
                    user_input=case["input"],
                    user_id=case.get("user_id"),
                    referenced_ids=case.get("referenced_ids"),
                    viewed_user_ids=[]
                )
                
                # 分析结果
                intent_analysis = result.get("intent_analysis", {})
                detected_intent = intent_analysis.get("intent", "unknown")
                processing_time = result.get("processing_time", 0)
                result_type = result.get("type", "unknown")
                
                print(f"  检测意图: {detected_intent}")
                print(f"  处理类型: {result_type}")
                print(f"  处理时间: {processing_time:.3f}秒")
                
                # 显示实际返回的内容
                print(f"\n  📄 返回结果详情:")
                if result.get("content"):
                    # 对于inquiry和chat模式，显示content内容
                    content = result.get("content", "")
                    print(f"    文本内容: {content[:200]}{'...' if len(content) > 200 else ''}")
                
                if result.get("candidates"):
                    # 对于search模式，显示候选人信息
                    candidates = result.get("candidates", [])
                    print(f"    找到候选人: {len(candidates)}个")
                    if candidates:
                        for j, candidate in enumerate(candidates[:2], 1):
                            name = candidate.get("name", "未知")
                            match_reason = candidate.get("match_reason", "无匹配原因")
                            print(f"      候选人{j}: {name} - {match_reason[:100]}{'...' if len(match_reason) > 100 else ''}")
                
                if result.get("intro_message"):
                    # 显示引导消息
                    intro = result.get("intro_message", "")
                    print(f"    引导消息: {intro[:150]}{'...' if len(intro) > 150 else ''}")
                
                # 显示完整的JSON结果（用于调试）
                print(f"\n  🔍 完整JSON结果:")
                import json
                try:
                    # 过滤掉一些冗余信息，只显示关键内容
                    filtered_result = {
                        "type": result.get("type"),
                        "intent": detected_intent,
                        "confidence": intent_analysis.get("confidence"),
                        "content": result.get("content"),
                        "candidate_count": len(result.get("candidates", [])),
                        "has_intro_message": bool(result.get("intro_message")),
                        "processing_time": processing_time
                    }
                    print(f"    {json.dumps(filtered_result, ensure_ascii=False, indent=4)}")
                except Exception as json_error:
                    print(f"    JSON序列化失败: {json_error}")
                
                # 验证功能是否正常工作
                success = False
                if result.get("content") or result.get("candidates"):
                    success = True
                    conversation_results["success"] += 1
                    print("  ✅ 智能交互成功")
                else:
                    print("  ⚠️ 智能交互返回空结果")
                
                conversation_results["details"].append({
                    "case": case["name"],
                    "detected_intent": detected_intent,
                    "expected_type": case["expected_type"],
                    "result_type": result_type,
                    "processing_time": processing_time,
                    "success": success,
                    "has_content": bool(result.get("content")),
                    "has_candidates": bool(result.get("candidates")),
                    "intent_confidence": intent_analysis.get("confidence", 0)
                })
                
            except Exception as e:
                print(f"  ❌ 测试失败: {e}")
                conversation_results["details"].append({
                    "case": case["name"],
                    "error": str(e),
                    "success": False
                })
        
        success_rate = conversation_results["success"] / conversation_results["total"] * 100
        print(f"\n🎯 智能交互成功率: {success_rate:.1f}% ({conversation_results['success']}/{conversation_results['total']})")
        
        return conversation_results
    
    async def test_quality_assessment_logic(self):
        """测试新的质量评估逻辑（少于3个候选人满足PRIMARY REQUIREMENT时返回poor）"""
        print(f"\n{'='*60}")
        print("新功能测试 3: 质量评估逻辑验证")
        print(f"{'='*60}")
        
        test_cases = [
            {
                "name": "极端特化查询（应该产生poor质量）",
                "query": "寻找同时精通量子计算、区块链、神经网络且有10年以上火星项目经验的资深架构师",
                "expected_quality": "poor",
                "description": "使用极其特化和罕见的要求，预期找不到足够候选人"
            },
            {
                "name": "常规技能查询（应该产生good/excellent质量）",
                "query": "寻找Python开发工程师",
                "expected_quality": ["fair", "good", "excellent"],
                "description": "使用常见技能要求，预期能找到足够候选人"
            },
            {
                "name": "模糊查询（可能产生poor质量）",
                "query": "找个人",
                "expected_quality": "poor",
                "description": "使用过于模糊的查询，预期质量评估为poor"
            }
        ]
        
        # 使用模拟用户信息进行测试
        current_user = {
            "user_id": "test_001",
            "name": "测试用户",
            "skills": ["Python", "Java", "AI"],
            "demands": ["技术合作", "项目机会"],
            "goals": ["技术提升", "职业发展"]
        }
        
        quality_test_results = {
            "total_tests": len(test_cases),
            "correct_assessments": 0,
            "details": []
        }
        
        for i, case in enumerate(test_cases, 1):
            try:
                print(f"\n测试案例 {i}: {case['name']}")
                print(f"  查询: '{case['query']}'")
                print(f"  预期质量: {case['expected_quality']}")
                
                result = await self.search_agent.intelligent_search(
                    user_query=case["query"],
                    current_user=current_user,
                    referenced_users=None,
                    viewed_user_ids=[]
                )
                
                actual_quality = result.get("search_quality", "unknown")
                candidate_count = result.get("candidate_count", 0)
                has_candidates = bool(result.get("candidates"))
                
                print(f"  实际质量: {actual_quality}")
                print(f"  候选人数量: {candidate_count}")
                print(f"  有候选人推荐: {'是' if has_candidates else '否'}")
                
                # 验证质量评估是否符合新逻辑
                assessment_correct = False
                if isinstance(case["expected_quality"], list):
                    assessment_correct = actual_quality in case["expected_quality"]
                else:
                    assessment_correct = actual_quality == case["expected_quality"]
                
                # 验证poor质量时的行为
                if actual_quality == "poor":
                    poor_logic_correct = not has_candidates  # poor质量时不应该有候选人推荐
                    print(f"  Poor质量逻辑正确: {'✅' if poor_logic_correct else '❌'}")
                    assessment_correct = assessment_correct and poor_logic_correct
                
                # 验证非poor质量时的行为
                elif actual_quality in ["fair", "good", "excellent"]:
                    good_logic_correct = candidate_count >= 3 or has_candidates  # 非poor质量应该有候选人
                    print(f"  好质量逻辑正确: {'✅' if good_logic_correct else '❌'}")
                    assessment_correct = assessment_correct and good_logic_correct
                
                if assessment_correct:
                    quality_test_results["correct_assessments"] += 1
                    print(f"  ✅ 质量评估正确")
                else:
                    print(f"  ❌ 质量评估不符合预期")
                
                quality_test_results["details"].append({
                    "case": case["name"],
                    "query": case["query"],
                    "expected_quality": case["expected_quality"],
                    "actual_quality": actual_quality,
                    "candidate_count": candidate_count,
                    "has_candidates": has_candidates,
                    "assessment_correct": assessment_correct
                })
                
            except Exception as e:
                print(f"  ❌ 测试失败: {e}")
                quality_test_results["details"].append({
                    "case": case["name"],
                    "error": str(e),
                    "assessment_correct": False
                })
        
        accuracy = quality_test_results["correct_assessments"] / quality_test_results["total_tests"] * 100
        print(f"\n🎯 质量评估逻辑准确率: {accuracy:.1f}% ({quality_test_results['correct_assessments']}/{quality_test_results['total_tests']})")
        
        return quality_test_results
    
    async def test_new_search_features(self):
        """测试新的搜索功能（使用current_user参数）"""
        print(f"\n{'='*60}")
        print("新功能测试 4: 更新的智能搜索功能")
        print(f"{'='*60}")
        
        # 获取一个随机用户作为当前用户
        current_user_id = self.get_random_user_id()
        
        # 先获取用户信息
        user_details = await self.search_agent._fetch_user_details_from_db([current_user_id])
        current_user = user_details.get(str(current_user_id))
        
        if current_user and not current_user.get('error'):
            print(f"✅ 获取到测试用户信息: {current_user.get('name', '未知用户')}")
        else:
            print(f"⚠️ 未能获取用户信息，使用模拟数据")
            current_user = {
                "user_id": current_user_id,
                "name": "测试用户",
                "skills": ["Python", "AI"],
                "demands": ["技术合作", "项目机会"],
                "goals": ["技术提升", "职业发展"]
            }
        
        test_query = "寻找有机器学习经验的Python开发工程师"
        
        try:
            print(f"\n执行搜索查询: '{test_query}'")
            
            result = await self.search_agent.intelligent_search(
                user_query=test_query,
                current_user=current_user,
                referenced_users=None,
                viewed_user_ids=[]
            )
            
            # 分析搜索结果的新功能特性
            search_analysis = {
                "has_candidates": bool(result.get("candidates")),
                "has_match_reasons": False,
                "has_intro_message": bool(result.get("intro_message")),
                "has_quality_analysis": bool(result.get("search_quality")),
                "candidate_count": result.get("candidate_count", 0),
                "search_quality": result.get("search_quality", "unknown"),
                "processing_time": result.get("search_time", 0)
            }
            
            # 检查匹配原因质量
            candidates = result.get("candidates", [])
            if candidates:
                reasons_with_natural_language = 0
                for candidate in candidates:
                    match_reason = candidate.get("match_reason", "")
                    if match_reason and len(match_reason) > 10:
                        search_analysis["has_match_reasons"] = True
                        # 检查是否使用自然语言而非机械化描述
                        if not any(phrase in match_reason for phrase in ["满足您的需求", "satisfies requirements"]):
                            reasons_with_natural_language += 1
                
                search_analysis["natural_language_ratio"] = reasons_with_natural_language / len(candidates) if candidates else 0
            
            print(f"\n📊 搜索功能分析:")
            print(f"  搜索质量: {search_analysis['search_quality']}")
            print(f"  找到候选人: {search_analysis['candidate_count']}个")
            print(f"  有匹配原因: {'✅' if search_analysis['has_match_reasons'] else '❌'}")
            print(f"  有引导消息: {'✅' if search_analysis['has_intro_message'] else '❌'}")
            print(f"  有质量分析: {'✅' if search_analysis['has_quality_analysis'] else '❌'}")
            print(f"  自然语言比例: {search_analysis.get('natural_language_ratio', 0):.1%}")
            print(f"  处理时间: {search_analysis['processing_time']:.2f}秒")
            
            # 验证新的质量评估逻辑
            if search_analysis['search_quality'] == 'poor':
                if search_analysis['candidate_count'] == 0:
                    print(f"  ✅ Poor质量逻辑正确: 无候选人推荐")
                else:
                    print(f"  ⚠️ Poor质量但仍有候选人，可能存在逻辑问题")
            elif search_analysis['search_quality'] in ['fair', 'good', 'excellent']:
                if search_analysis['candidate_count'] >= 3:
                    print(f"  ✅ 质量评估逻辑正确: {search_analysis['candidate_count']}个候选人满足要求")
                else:
                    print(f"  ⚠️ 非poor质量但候选人不足3个，需要检查逻辑")
            
            if search_analysis["has_candidates"]:
                print("\n👥 候选人匹配原因示例:")
                for i, candidate in enumerate(candidates[:2], 1):
                    match_reason = candidate.get("match_reason", "无")
                    print(f"  候选人{i}: {match_reason}")
            
            return search_analysis
            
        except Exception as e:
            print(f"❌ 搜索测试失败: {e}")
            return {"error": str(e), "success": False}
    
    # ===== 原有的搜索测试方法（简化版） =====
    
    
    async def run_comprehensive_tests(self):
        """运行综合测试套件，重点测试新功能"""
        print("🚀 开始智能搜索代理集成测试")
        print(f"使用集合: users_rawjson")
        print("重点关注新增的智能交互功能")
        
        # 运行新功能测试
        print(f"\n{'🆕'*20} 新功能测试 {'🆕'*20}")
        
        # 1. 测试意图识别
        intent_results = await self.test_intent_analysis()
        
        # 2. 测试智能交互统一入口
        conversation_results = await self.test_intelligent_conversation()
        
        # 3. 测试新的质量评估逻辑
        quality_results = await self.test_quality_assessment_logic()
        
        # 4. 测试更新的搜索功能
        search_results = await self.test_new_search_features()
        
        # 运行少量传统搜索测试作为对比
        print(f"\n{'📊'*20} 传统搜索测试对比 {'📊'*20}")
        
        traditional_test_cases = [
            {
                "name": "技能搜索对比",
                "query": "寻找Python开发工程师",
                "user_id": self.get_random_user_id(),
            },
            {
                "name": "复合条件搜索对比", 
                "query": "找一个在北京的AI算法工程师",
                "user_id": self.get_random_user_id(),
            }
        ]
        
        traditional_results = []
        for test_case in traditional_test_cases:
            try:
                user_details = await self.search_agent._fetch_user_details_from_db([test_case["user_id"]])
                current_user = user_details.get(str(test_case["user_id"]))
                
                result = await self.search_agent.intelligent_search(
                    user_query=test_case["query"],
                    current_user=current_user,
                    viewed_user_ids=[]
                )
                
                traditional_results.append({
                    "name": test_case["name"],
                    "success": result.get("status") == "success",
                    "candidate_count": result.get("candidate_count", 0),
                    "search_time": result.get("search_time", 0)
                })
                
                print(f"✅ {test_case['name']}: {result.get('candidate_count', 0)}个候选人, {result.get('search_time', 0):.2f}秒")
                
            except Exception as e:
                print(f"❌ {test_case['name']}: {e}")
                traditional_results.append({
                    "name": test_case["name"],
                    "success": False,
                    "error": str(e)
                })
        
        # 生成新功能测试报告
        self.generate_new_features_report(intent_results, conversation_results, quality_results, search_results, traditional_results)
    
    def generate_new_features_report(self, intent_results, conversation_results, quality_results, search_results, traditional_results):
        """生成专注于新功能的测试报告"""
        print(f"\n{'='*80}")
        print("🎯 新功能测试报告")
        print(f"{'='*80}")
        
        # 意图识别分析
        print(f"\n1️⃣ 意图识别系统评估:")
        intent_accuracy = intent_results["correct"] / intent_results["total"] * 100
        print(f"   准确率: {intent_accuracy:.1f}% ({intent_results['correct']}/{intent_results['total']})")
        
        if intent_accuracy >= 80:
            print(f"   ✅ 意图识别表现优秀")
        elif intent_accuracy >= 60:
            print(f"   ⚠️ 意图识别表现一般，需要优化")
        else:
            print(f"   ❌ 意图识别表现较差，需要重点改进")
        
        # 按意图类型分析
        intent_by_type = {}
        for detail in intent_results["details"]:
            expected = detail.get("expected", "unknown")
            if expected not in intent_by_type:
                intent_by_type[expected] = {"correct": 0, "total": 0}
            intent_by_type[expected]["total"] += 1
            if detail.get("correct", False):
                intent_by_type[expected]["correct"] += 1
        
        print(f"   按意图类型分析:")
        for intent_type, stats in intent_by_type.items():
            accuracy = stats["correct"] / stats["total"] * 100 if stats["total"] > 0 else 0
            print(f"     {intent_type}: {accuracy:.1f}% ({stats['correct']}/{stats['total']})")
        
        # 智能交互评估
        print(f"\n2️⃣ 智能交互统一入口评估:")
        conversation_success = conversation_results["success"] / conversation_results["total"] * 100
        print(f"   成功率: {conversation_success:.1f}% ({conversation_results['success']}/{conversation_results['total']})")
        
        avg_processing_time = 0
        valid_times = [d.get("processing_time", 0) for d in conversation_results["details"] if d.get("processing_time", 0) > 0]
        if valid_times:
            avg_processing_time = sum(valid_times) / len(valid_times)
            print(f"   平均处理时间: {avg_processing_time:.3f}秒")
        
        if conversation_success >= 90:
            print(f"   ✅ 智能交互功能工作正常")
        else:
            print(f"   ⚠️ 智能交互功能需要检查")
        
        # 质量评估逻辑评估
        print(f"\n3️⃣ 质量评估逻辑评估:")
        quality_accuracy = quality_results["correct_assessments"] / quality_results["total_tests"] * 100
        print(f"   准确率: {quality_accuracy:.1f}% ({quality_results['correct_assessments']}/{quality_results['total_tests']})")
        
        # 分析具体的质量评估表现
        poor_cases = [d for d in quality_results["details"] if d.get("actual_quality") == "poor"]
        good_cases = [d for d in quality_results["details"] if d.get("actual_quality") in ["fair", "good", "excellent"]]
        
        print(f"   Poor质量案例: {len(poor_cases)}个")
        for case in poor_cases:
            has_candidates = case.get("has_candidates", False)
            print(f"     - {case.get('case', '未知')}: {'✅ 正确(无候选人)' if not has_candidates else '❌ 错误(仍有候选人)'}")
        
        print(f"   良好质量案例: {len(good_cases)}个")
        for case in good_cases:
            candidate_count = case.get("candidate_count", 0)
            print(f"     - {case.get('case', '未知')}: {candidate_count}个候选人 ({'✅ 符合逻辑' if candidate_count >= 3 else '⚠️ 数量不足'})")
        
        if quality_accuracy >= 80:
            print(f"   ✅ 质量评估逻辑工作正常")
        elif quality_accuracy >= 60:
            print(f"   ⚠️ 质量评估逻辑基本正常，需要微调")
        else:
            print(f"   ❌ 质量评估逻辑需要重点优化")
        
        # 新搜索功能评估
        print(f"\n4️⃣ 增强搜索功能评估:")
        if search_results.get("error"):
            print(f"   ❌ 搜索功能测试失败: {search_results['error']}")
        else:
            print(f"   搜索质量: {search_results.get('search_quality', '未知')}")
            print(f"   候选人数量: {search_results.get('candidate_count', 0)}")
            print(f"   匹配原因功能: {'✅ 正常' if search_results.get('has_match_reasons') else '❌ 异常'}")
            print(f"   引导消息功能: {'✅ 正常' if search_results.get('has_intro_message') else '❌ 异常'}")
            print(f"   质量分析功能: {'✅ 正常' if search_results.get('has_quality_analysis') else '❌ 异常'}")
            
            natural_ratio = search_results.get('natural_language_ratio', 0)
            if natural_ratio >= 0.8:
                print(f"   自然语言表达: ✅ 优秀 ({natural_ratio:.1%})")
            elif natural_ratio >= 0.5:
                print(f"   自然语言表达: ⚠️ 一般 ({natural_ratio:.1%})")
            else:
                print(f"   自然语言表达: ❌ 需要改进 ({natural_ratio:.1%})")
        
        # 传统搜索对比
        print(f"\n5️⃣ 传统搜索功能对比:")
        traditional_success = len([r for r in traditional_results if r.get("success", False)])
        print(f"   基础搜索成功率: {traditional_success}/{len(traditional_results)}")
        
        total_candidates = sum([r.get("candidate_count", 0) for r in traditional_results if r.get("success")])
        avg_candidates = total_candidates / max(traditional_success, 1)
        print(f"   平均候选人数量: {avg_candidates:.1f}")
        
        # 总体评估
        print(f"\n🎯 总体新功能评估:")
        
        feature_scores = []
        if intent_accuracy >= 70:
            feature_scores.append("✅ 意图识别")
        else:
            feature_scores.append("❌ 意图识别")
            
        if conversation_success >= 80:
            feature_scores.append("✅ 智能交互")
        else:
            feature_scores.append("❌ 智能交互")
            
        if quality_accuracy >= 70:
            feature_scores.append("✅ 质量评估逻辑")
        else:
            feature_scores.append("❌ 质量评估逻辑")
            
        if not search_results.get("error") and search_results.get("has_match_reasons"):
            feature_scores.append("✅ 增强搜索")
        else:
            feature_scores.append("❌ 增强搜索")
        
        working_features = len([s for s in feature_scores if s.startswith("✅")])
        total_features = len(feature_scores)
        
        print(f"   工作正常的新功能: {working_features}/{total_features}")
        for score in feature_scores:
            print(f"   {score}")
        
        if working_features == total_features:
            print(f"\n🎉 所有新功能都工作正常！系统升级成功。")
        elif working_features >= total_features * 0.7:
            print(f"\n⚠️ 大部分新功能工作正常，少数功能需要调试。")
        else:
            print(f"\n🔧 多个新功能需要修复，建议进一步调试。")
        
        print(f"\n{'='*80}")
        print("📋 建议后续步骤:")
        print("1. 如果LLM调用失败，请检查API密钥和网络连接")
        print("2. 如果意图识别不准确，可以调整prompt模板")
        print("3. 如果质量评估逻辑不准确，检查PRIMARY REQUIREMENT的匹配标准")
        print("4. 如果搜索结果为空，请检查Qdrant数据库连接")
        print("5. 查看详细错误日志进行针对性优化")
        print(f"{'='*80}")


async def main():
    """主函数"""
    test_suite = IntegrationTestSuite()
    await test_suite.run_comprehensive_tests()


if __name__ == "__main__":
    asyncio.run(main())