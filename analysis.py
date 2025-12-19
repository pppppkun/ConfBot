import pandas as pd
import numpy as np

class PaperAnalyzer:
    def __init__(self, df):
        """
        初始化分析器，传入原始 DataFrame
        """
        self.raw_df = df
        # 预处理：填充空值，防止后续报错
        # 针对你的数据，keywords 可能是空的，这步很重要
        if 'keywords' in self.raw_df.columns:
            self.raw_df['keywords'] = self.raw_df['keywords'].fillna('')
        if 'authors' in self.raw_df.columns:
            self.raw_df['authors'] = self.raw_df['authors'].fillna('')

    @staticmethod
    def load_data(file_path=None):
        """
        加载数据函数。
        """
        if file_path:
            # --- 真实模式 ---
            try:
                # pandas 的 read_csv 默认能完美处理你数据中的双引号
                # 例如 "Kathryn Stolee,Tobias Welp" 会被正确读作一个字符串
                df = pd.read_csv(file_path, encoding='utf-8')
                return df
            except Exception as e:
                print(f"读取文件失败: {e}")
                # 尝试使用 gbk 编码，防止中文系统下的编码问题
                try:
                    print("尝试使用 gbk 编码读取...")
                    df = pd.read_csv(file_path, encoding='gbk')
                    return df
                except:
                    return pd.DataFrame()
        else:
            # --- 模拟模式 (生成符合你格式的数据用于测试) ---
            return pd.DataFrame()

    def _explode_column(self, df, col_name):
        """
        内部工具函数：将包含多个值的字符串列炸开成多行
        针对你的数据格式：Authors 是用逗号分隔的
        """
        df_exploded = df.copy()
        
        # 确保列存在且为字符串类型
        if col_name not in df_exploded.columns:
            return df_exploded
            
        df_exploded[col_name] = df_exploded[col_name].astype(str)
        
        # 核心逻辑：你的数据是用逗号分隔的，例如 "Author A,Author B"
        # 我们先将 '，' (中文逗号) 和 分号 统一替换为英文逗号
        df_exploded[col_name] = df_exploded[col_name].str.replace(';', ',').str.replace('，', ',')
        
        # 按照逗号分割
        df_exploded[col_name] = df_exploded[col_name].str.split(',')
        
        # 炸开列表
        df_exploded = df_exploded.explode(col_name)
        
        # 去除前后空格 (处理 "Author A, Author B" 这种情况)
        df_exploded[col_name] = df_exploded[col_name].str.strip()
        
        # 过滤掉空字符串
        return df_exploded[df_exploded[col_name] != '']

    def get_basic_info(self):
        """返回基础统计信息"""
        if self.raw_df.empty:
            return {'total_papers': 0, 'year_range': (0, 0), 'conferences': [], 'years': []}
            
        return {
            'total_papers': len(self.raw_df),
            'year_range': (self.raw_df['year'].min(), self.raw_df['year'].max()),
            'conferences': self.raw_df['conference'].unique().tolist(),
            'years': sorted(self.raw_df['year'].unique(), reverse=True)
        }

    def get_keyword_stats(self, year=None, conference=None, limit=None):
        """
        统计关键词频率
        """
        df_subset = self.raw_df.copy()
        if year:
            df_subset = df_subset[df_subset['year'] == year]
        if conference:
            df_subset = df_subset[df_subset['conference'] == conference]
            
        if df_subset.empty:
            return pd.DataFrame(), df_subset

        # 炸开 keywords 列
        df_exploded = self._explode_column(df_subset, 'keywords')
        
        if df_exploded.empty:
            return pd.DataFrame(columns=['Keyword', 'Count']), df_subset

        # 统计
        stats = df_exploded['keywords'].value_counts().reset_index()
        stats.columns = ['Keyword', 'Count']
        
        if limit:
            stats = stats.head(limit)
            
        return stats, df_subset

    def get_papers_by_keyword_strict(self, keyword, df_scope=None):
        """
        查找包含特定关键词的论文
        """
        target_df = df_scope if df_scope is not None else self.raw_df
        # 模糊匹配
        return target_df[target_df['keywords'].str.contains(keyword, case=False, na=False)]

    def get_authors_by_keyword(self, keyword):
        """
        针对特定关键词，统计相关作者
        """
        relevant_papers = self.get_papers_by_keyword_strict(keyword)
        
        if relevant_papers.empty:
            return pd.DataFrame(), relevant_papers

        # 炸开 authors 列
        df_exploded = self._explode_column(relevant_papers, 'authors')
        
        # 统计 authors 频率
        stats = df_exploded['authors'].value_counts().reset_index()
        stats.columns = ['Author', 'Paper_Count']
        
        return stats, relevant_papers

    def get_author_profile(self, author_name):
        """
        获取特定作者的所有论文及统计信息
        """
        # 匹配 authors 列
        papers = self.raw_df[self.raw_df['authors'].str.contains(author_name, case=False, na=False)]
        
        # 统计 conference 分布
        conf_dist = papers['conference'].value_counts().reset_index()
        conf_dist.columns = ['Conference', 'Count']
        
        # 统计 year 分布
        if not papers.empty:
            min_year, max_year = self.raw_df['year'].min(), self.raw_df['year'].max()
            year_trend = papers.groupby('year').size().reset_index(name='Count')
            all_years = pd.DataFrame({'year': range(min_year, max_year + 1)})
            year_trend = pd.merge(all_years, year_trend, on='year', how='left').fillna(0)
        else:
            year_trend = pd.DataFrame()

        return papers, conf_dist, year_trend

    def get_all_authors_list(self):
        """获取所有不重复的作者列表"""
        df_exploded = self._explode_column(self.raw_df, 'authors')
        return sorted(df_exploded['authors'].unique().tolist())

    def get_all_keywords_list(self):
        """获取所有不重复的关键词列表"""
        df_exploded = self._explode_column(self.raw_df, 'keywords')
        return df_exploded['keywords'].value_counts().index.tolist()
    

    def get_keyword_trend_data(self, conference=None, top_n=20):
        """
        获取关键词随时间变化的趋势数据（用于画折线图）
        逻辑：
        1. 筛选会议（可选）。
        2. 统计所有年份中，出现总频次最高的 Top N 个关键词。
        3. 返回这些关键词在每一年的具体频次数据。
        """
        df_subset = self.raw_df.copy()
        if conference:
            df_subset = df_subset[df_subset['conference'] == conference]
        
        if df_subset.empty:
            return pd.DataFrame()

        # 1. 炸开关键词
        df_exploded = self._explode_column(df_subset, 'keywords')
        
        # 2. 找出全时段最热的 Top N 关键词
        global_top = df_exploded['keywords'].value_counts().head(top_n).index.tolist()
        
        # 3. 统计每一年这些关键词的频率
        # 过滤只保留 Top N 关键词
        df_filtered = df_exploded[df_exploded['keywords'].isin(global_top)]
        
        # 按年份和关键词分组统计
        trend_data = df_filtered.groupby(['year', 'keywords']).size().reset_index(name='Count')
        
        # 补全数据：确保每个关键词在每一年都有记录（没有的填0），以便画图连续
        # Pivot table: Index=Year, Columns=Keywords, Values=Count
        pivot_df = trend_data.pivot(index='year', columns='keywords', values='Count').fillna(0)
        
        # 还原为长格式 (Melt) 以便 Plotly 使用
        trend_final = pivot_df.reset_index().melt(id_vars='year', var_name='Keyword', value_name='Count')
        
        return trend_final

    def get_yearly_top_k_matrix(self, conference=None, k=20):
        """
        生成一个“年度排名矩阵”表格
        列是年份，行是排名(1~k)，单元格内容是 "关键词 (频次)"
        用于直观对比每年的榜单变化
        """
        df_subset = self.raw_df.copy()
        if conference:
            df_subset = df_subset[df_subset['conference'] == conference]
            
        if df_subset.empty:
            return pd.DataFrame()

        df_exploded = self._explode_column(df_subset, 'keywords')
        
        # 按年份分组处理
        years = sorted(df_exploded['year'].unique(), reverse=True)
        result_dict = {}
        
        for year in years:
            # 获取该年的数据
            df_year = df_exploded[df_exploded['year'] == year]
            # 统计并排序
            top_k = df_year['keywords'].value_counts().head(k).reset_index()
            top_k.columns = ['Keyword', 'Count']
            
            # 格式化显示文本: "Deep Learning (45)"
            # 如果不足 k 个，用空字符串填充
            col_data = []
            for i in range(k):
                if i < len(top_k):
                    row = top_k.iloc[i]
                    col_data.append(f"{row['Keyword']} ({row['Count']})")
                else:
                    col_data.append("-")
            
            result_dict[year] = col_data
            
        # 生成 DataFrame，索引是排名 1~k
        rank_df = pd.DataFrame(result_dict)
        rank_df.index = [f"Top {i+1}" for i in range(k)]
        
        return rank_df    
    

    def get_author_keyword_details(self, author_papers):
        """
        输入: 该作者的所有论文 DataFrame (通过 get_author_profile 获取的)
        输出: 
            1. kw_counts: 关键词总频次排名
            2. kw_trend: 关键词随年份变化的详细数据 (用于气泡图/热力图)
        """
        if author_papers.empty:
            return pd.DataFrame(), pd.DataFrame()
            
        # 1. 炸开关键词
        df_exploded = self._explode_column(author_papers, 'keywords')
        
        if df_exploded.empty:
            return pd.DataFrame(), pd.DataFrame()

        # 2. 统计总频次 (列名设为 Keyword)
        kw_counts = df_exploded['keywords'].value_counts().reset_index()
        kw_counts.columns = ['Keyword', 'Count']
        
        # 3. 统计年度变化 (Year, keywords, Count)
        kw_trend = df_exploded.groupby(['year', 'keywords']).size().reset_index(name='Count')
        
        # === 修复点: 将小写 keywords 重命名为大写 Keyword，以便与 kw_counts 匹配 ===
        kw_trend = kw_trend.rename(columns={'keywords': 'Keyword'})
        
        # 4. 合并 (现在两边都有 Keyword 列了)
        kw_trend = pd.merge(kw_trend, kw_counts, on='Keyword', suffixes=('_Year', '_Total'))
        
        return kw_counts, kw_trend