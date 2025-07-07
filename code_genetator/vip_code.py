import pandas as pd
import random
import string
import os
from datetime import datetime

def generate_unique_card_numbers(count=5000):
    """生成指定数量的唯一会员卡号"""
    card_numbers = set()
    exclude_letters = {'I', 'O'}
    available_letters = [char for char in string.ascii_uppercase if char not in exclude_letters]
    
    print(f"开始生成{count}个会员卡号...")
    progress_step = max(1, count // 10)  # 每10%显示一次进度
    
    while len(card_numbers) < count:
        # 显示进度
        if len(card_numbers) % progress_step == 0 and len(card_numbers) > 0:
            progress = len(card_numbers) / count * 100
            print(f"已生成: {len(card_numbers)}/{count} ({progress:.1f}%)")
        
        # 生成5位随机数字（补零到5位）
        random_digits = f"{random.randint(0, 99999):05d}"
        # 随机选择1个有效字母
        random_letter = random.choice(available_letters)
        # 组合卡号
        card_number = f"V8{random_digits}{random_letter}"
        card_numbers.add(card_number)
    
    print(f"成功生成{len(card_numbers)}个唯一卡号！")
    return card_numbers

def save_to_excel(card_numbers, filename="会员卡号列表.xlsx"):
    """保存卡号到Excel文件"""
    # 确保中文显示正常
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    pd.set_option('display.unicode.east_asian_width', True)
    
    df = pd.DataFrame(list(card_numbers), columns=['会员卡号'])
    
    # 添加创建时间列
    df['生成时间'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 保存Excel文件
    try:
        df.to_excel(filename, index=False)
        file_size = os.path.getsize(filename) / 1024  # KB
        print(f"✅ 已保存至: {filename} ({file_size:.2f}KB)")
        print(f"文件位置: {os.path.abspath(filename)}")
    except Exception as e:
        print(f"❌ 保存失败: {str(e)}")
        # 保存为CSV作为备选
        csv_filename = filename.replace('.xlsx', '.csv')
        try:
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            print(f"⚠️ 已保存为CSV格式: {csv_filename}")
        except Exception as e2:
            print(f"❌ CSV保存也失败: {str(e2)}")
            print("请检查文件权限或尝试关闭已打开的文件")

def main():
    """主函数"""
    print("="*50)
    print("          会员卡号生成工具          ")
    print("="*50)
    
    # 配置参数
    CARD_COUNT = 5000
    OUTPUT_FILE = f"会员卡号_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
    
    try:
        # 生成卡号
        card_numbers = generate_unique_card_numbers(CARD_COUNT)
        
        # 保存到Excel
        save_to_excel(card_numbers, OUTPUT_FILE)
        
        print("\n操作完成！")
    except KeyboardInterrupt:
        print("\n⚠️ 程序被用户中断")
    except Exception as e:
        print(f"❌ 发生错误: {str(e)}")

if __name__ == "__main__":
    main()