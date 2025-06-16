"""
初始化数据库脚本
创建默认管理员和基础数据
"""
import asyncio
from tortoise import Tortoise
from app.config import TORTOISE_ORM
from app.models.admin import Admin
from app.models.semester import Semester
from app.models.grade import Grade
from app.models.subject import Subject
from app.utils.auth import get_password_hash


async def init_db():
    """初始化数据库"""
    # 初始化Tortoise ORM
    await Tortoise.init(config=TORTOISE_ORM)
    
    # 生成数据库表
    await Tortoise.generate_schemas()
    
    # 创建默认超级管理员
    admin_exists = await Admin.filter(username="admin").exists()
    if not admin_exists:
        await Admin.create(
            username="admin",
            email="admin@hqxx.edu.cn",
            hashed_password=get_password_hash("admin123"),
            full_name="系统管理员",
            is_active=True,
            is_superuser=True
        )
        print("✅ 创建默认管理员: admin / admin123")
    
    # 创建默认学期
    semester_exists = await Semester.exists()
    if not semester_exists:
        semesters = [
            {"name": "2024年春季学期", "code": "2024S", "sort_order": 1},
            {"name": "2024年秋季学期", "code": "2024F", "sort_order": 2},
        ]
        for semester_data in semesters:
            await Semester.create(**semester_data)
        print("✅ 创建默认学期数据")
    
    # 创建默认年级
    grade_exists = await Grade.exists()
    if not grade_exists:
        grades = [
            {"name": "一年级", "code": "G1", "level": 1, "sort_order": 1},
            {"name": "二年级", "code": "G2", "level": 2, "sort_order": 2},
            {"name": "三年级", "code": "G3", "level": 3, "sort_order": 3},
            {"name": "四年级", "code": "G4", "level": 4, "sort_order": 4},
            {"name": "五年级", "code": "G5", "level": 5, "sort_order": 5},
            {"name": "六年级", "code": "G6", "level": 6, "sort_order": 6},
        ]
        for grade_data in grades:
            await Grade.create(**grade_data)
        print("✅ 创建默认年级数据")
    
    # 创建默认学科
    subject_exists = await Subject.exists()
    if not subject_exists:
        subjects = [
            {"name": "语文", "code": "chinese", "color": "#ff6b6b", "sort_order": 1},
            {"name": "数学", "code": "math", "color": "#4ecdc4", "sort_order": 2},
            {"name": "英语", "code": "english", "color": "#45b7d1", "sort_order": 3},
            {"name": "科学", "code": "science", "color": "#96ceb4", "sort_order": 4},
            {"name": "道德与法治", "code": "moral", "color": "#feca57", "sort_order": 5},
        ]
        for subject_data in subjects:
            await Subject.create(**subject_data)
        print("✅ 创建默认学科数据")
    
    # 创建默认分类
    from app.models.category import Category
    category_exists = await Category.exists()
    if not category_exists:
        # 获取学科
        chinese = await Subject.filter(code="chinese").first()
        math = await Subject.filter(code="math").first()

        if chinese:
            categories_data = [
                {"name": "拼音", "code": "pinyin", "subject": chinese, "sort_order": 1},
                {"name": "识字", "code": "words", "subject": chinese, "sort_order": 2},
                {"name": "阅读理解", "code": "reading", "subject": chinese, "sort_order": 3},
            ]
            for cat_data in categories_data:
                await Category.create(**cat_data)

        if math:
            categories_data = [
                {"name": "加减法", "code": "addition", "subject": math, "sort_order": 1},
                {"name": "乘除法", "code": "multiplication", "subject": math, "sort_order": 2},
                {"name": "应用题", "code": "word_problems", "subject": math, "sort_order": 3},
            ]
            for cat_data in categories_data:
                await Category.create(**cat_data)

        print("✅ 创建默认分类数据")

    # 创建测试题目
    from app.models.question import Question
    question_exists = await Question.exists()
    if not question_exists:
        # 获取基础数据
        semester = await Semester.filter(code="2024S").first()
        grade = await Grade.filter(code="G1").first()
        chinese = await Subject.filter(code="chinese").first()
        math = await Subject.filter(code="math").first()

        if semester and grade and chinese and math:
            # 获取分类
            pinyin_cat = await Category.filter(code="pinyin").first()
            addition_cat = await Category.filter(code="addition").first()

            if pinyin_cat:
                questions_data = [
                    {
                        "title": "拼音练习：声母b",
                        "content": "<p>请读出下面的拼音：<br><strong>ba  bi  bu  bo</strong></p>",
                        "answer": "ba读作巴，bi读作比，bu读作不，bo读作波",
                        "difficulty": 1,
                        "semester": semester,
                        "grade": grade,
                        "subject": chinese,
                        "category": pinyin_cat,
                        "is_published": True
                    },
                    {
                        "title": "拼音练习：韵母a",
                        "content": "<p>请读出下面的拼音：<br><strong>ma  fa  la  da</strong></p>",
                        "answer": "ma读作妈，fa读作发，la读作拉，da读作大",
                        "difficulty": 1,
                        "semester": semester,
                        "grade": grade,
                        "subject": chinese,
                        "category": pinyin_cat,
                        "is_published": True
                    }
                ]
                for q_data in questions_data:
                    await Question.create(**q_data)

            if addition_cat:
                questions_data = [
                    {
                        "title": "10以内加法：5+3",
                        "content": "<p>计算下面的加法题：</p><h2>5 + 3 = ?</h2>",
                        "difficulty": 1,
                        "semester": semester,
                        "grade": grade,
                        "subject": math,
                        "category": addition_cat,
                        "is_published": True
                    },
                    {
                        "title": "10以内加法：7+2",
                        "content": "<p>计算下面的加法题：</p><h2>7 + 2 = ?</h2>",
                        "difficulty": 1,
                        "semester": semester,
                        "grade": grade,
                        "subject": math,
                        "category": addition_cat,
                        "is_published": True
                    }
                ]
                for q_data in questions_data:
                    await Question.create(**q_data)

        print("✅ 创建测试题目数据")

    # 创建默认模板
    from app.models.template import Template
    template_exists = await Template.exists()
    if not template_exists:
        # 获取学科
        chinese = await Subject.filter(code="chinese").first()
        math = await Subject.filter(code="math").first()

        templates_data = [
            {
                "name": "拼音练习",
                "description": "带声调的拼音练习模板",
                "content": """
                <div style="text-align: center; margin: 20px 0; padding: 20px; border: 2px dashed #409eff; border-radius: 10px;">
                  <h3 style="color: #409eff; margin-bottom: 20px;">📖 拼音练习</h3>
                  <p style="margin-bottom: 15px; color: #606266;">请读出下面的拼音：</p>
                  <div style="font-size: 36px; letter-spacing: 8px; margin: 30px 0; line-height: 1.8;">
                    bā  bí  bǔ  bò
                  </div>
                  <div style="margin-top: 20px; font-size: 14px; color: #909399;">
                    提示：注意声调的准确性
                  </div>
                </div>
                """,
                "category": "语文",
                "icon": "🔤",
                "subject": chinese,
                "is_system": True,
                "sort_order": 1
            },
            {
                "name": "汉字练习",
                "description": "大字号汉字显示模板",
                "content": """
                <div style="text-align: center; margin: 20px 0; padding: 20px; border: 2px dashed #f56c6c; border-radius: 10px;">
                  <h3 style="color: #f56c6c; margin-bottom: 20px;">✍️ 汉字练习</h3>
                  <p style="margin-bottom: 15px; color: #606266;">请读出下面的汉字：</p>
                  <div style="font-size: 48px; letter-spacing: 20px; margin: 30px 0; line-height: 1.5;">
                    大  小  多  少
                  </div>
                  <div style="margin-top: 20px; font-size: 14px; color: #909399;">
                    提示：注意笔画顺序
                  </div>
                </div>
                """,
                "category": "语文",
                "icon": "📝",
                "subject": chinese,
                "is_system": True,
                "sort_order": 2
            },
            {
                "name": "数学计算",
                "description": "带答题区域的计算题",
                "content": """
                <div style="text-align: center; margin: 20px 0; padding: 20px; border: 2px dashed #e6a23c; border-radius: 10px;">
                  <h3 style="color: #e6a23c; margin-bottom: 20px;">🔢 数学计算</h3>
                  <p style="margin-bottom: 15px; color: #606266;">计算下面的题目：</p>
                  <div style="font-size: 32px; margin: 30px 0; line-height: 2;">
                    5 + 3 = <span style="border-bottom: 2px solid #333; padding: 0 20px; margin: 0 10px;"></span>
                  </div>
                  <div style="margin-top: 20px; font-size: 14px; color: #909399;">
                    请在横线上写出答案
                  </div>
                </div>
                """,
                "category": "数学",
                "icon": "🔢",
                "subject": math,
                "is_system": True,
                "sort_order": 3
            },
            {
                "name": "选择题",
                "description": "标准ABCD选择题格式",
                "content": """
                <div style="margin: 20px 0; padding: 20px; border: 2px dashed #909399; border-radius: 10px;">
                  <h3 style="color: #909399; margin-bottom: 15px;">☑️ 选择题</h3>
                  <p style="margin-bottom: 15px; font-weight: bold;">题目：请选择正确答案</p>
                  <div style="margin-left: 20px; line-height: 2;">
                    <p>A. 选项一</p>
                    <p>B. 选项二</p>
                    <p>C. 选项三</p>
                    <p>D. 选项四</p>
                  </div>
                  <div style="margin-top: 15px; font-size: 14px; color: #909399;">
                    答案：<span style="border-bottom: 1px solid #333; padding: 0 10px;"></span>
                  </div>
                </div>
                """,
                "category": "通用",
                "icon": "☑️",
                "is_system": True,
                "sort_order": 4
            },
            {
                "name": "填空题",
                "description": "带下划线的填空格式",
                "content": """
                <div style="margin: 20px 0; padding: 20px; border: 2px dashed #67c23a; border-radius: 10px;">
                  <h3 style="color: #67c23a; margin-bottom: 15px;">✏️ 填空题</h3>
                  <p style="line-height: 2.5;">
                    请在横线上填入合适的词语：<br><br>
                    春天来了，<span style="border-bottom: 2px solid #333; padding: 0 30px; margin: 0 5px;"></span>开花了，
                    <span style="border-bottom: 2px solid #333; padding: 0 30px; margin: 0 5px;"></span>变绿了。
                  </p>
                </div>
                """,
                "category": "通用",
                "icon": "✏️",
                "is_system": True,
                "sort_order": 5
            }
        ]

        for template_data in templates_data:
            await Template.create(**template_data)

        print("✅ 创建默认模板数据")

    print("🎉 数据库初始化完成!")

    # 关闭连接
    await Tortoise.close_connections()


if __name__ == "__main__":
    asyncio.run(init_db())
