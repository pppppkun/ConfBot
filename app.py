import streamlit as st
import plotly.express as px
import pandas as pd
from analysis import PaperAnalyzer

# ==========================================
# 0. 页面配置与数据加载
# ==========================================
st.set_page_config(page_title="学术论文数据分析看板", layout="wide", page_icon="📊")

@st.cache_data
def load_data_cached():
    # TODO: 请在这里将 path 替换为你的真实 CSV 文件路径
    path = 'meta.csv'  # 例如 "data/my_papers.csv"
    df = PaperAnalyzer.load_data(path)
    return df

# 初始化
try:
    df_raw = load_data_cached()
    analyzer = PaperAnalyzer(df_raw)
    basic_info = analyzer.get_basic_info()
    all_unique_kws = analyzer.get_all_keywords_list()
except Exception as e:
    st.error(f"数据加载失败，请检查 analysis.py 中的路径设置。错误: {e}")
    st.stop()

# ==========================================
# 1. 侧边栏
# ==========================================
with st.sidebar:
    st.header("📊 数据概览")
    st.info(f"📚 总论文数: {basic_info['total_papers']}")
    st.info(f"⏳ 年份范围: {basic_info['year_range'][0]} - {basic_info['year_range'][1]}")
    st.info(f"🏛️ 涵盖会议: {len(basic_info['conferences'])} 个")
    st.info(f"🔑 关键词总数: {len(all_unique_kws)} 个")
    
    st.markdown("---")
    if st.checkbox("显示所有关键词列表"):
        st.write("所有出现过的关键词：")
        st.dataframe(pd.DataFrame(all_unique_kws, columns=["Keywords"]), use_container_width=True)

st.title("📚 学术论文多维数据分析看板")

# ==========================================
# 2. 核心功能区
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📅 年度关键词热度", 
    "🏛️ 会议关键词分析", 
    "👥 关键词下的作者", 
    "👤 作者投稿画像",
    "📈 关键词趋势分析" 
])

# --- 功能 1: 年度关键词 ---
with tab1:
    st.subheader("1. 年度关键词流行度分析")
    selected_year = st.selectbox("选择年份", basic_info['years'], key="t1_year")
    
    kw_stats, df_year_scope = analyzer.get_keyword_stats(year=selected_year, limit=20)
    
    if not kw_stats.empty:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**{selected_year} Top 20 关键词分布**")
            fig_bar = px.bar(kw_stats, x='Keyword', y='Count', color='Count', 
                             color_continuous_scale='Blues', text='Count')
            st.plotly_chart(fig_bar, use_container_width=True)
            
            fig_tree = px.treemap(kw_stats, path=['Keyword'], values='Count',
                                  color='Count', color_continuous_scale='RdBu')
            st.plotly_chart(fig_tree, use_container_width=True)

        with col2:
            st.write("**点击查看具体论文**")
            all_year_kws, _ = analyzer.get_keyword_stats(year=selected_year, limit=None)
            target_kw = st.selectbox("选择关键词查看详情:", all_year_kws['Keyword'].tolist())
            
            if target_kw:
                papers = analyzer.get_papers_by_keyword_strict(target_kw, df_scope=df_year_scope)
                st.write(f"关于 **{target_kw}** 的论文 ({len(papers)}篇):")
                for _, row in papers.iterrows():
                    with st.expander(f"{row['title']}"):
                        st.caption(f"Authors: {row['authors']}")
                        st.write(row['abstract'])
    else:
        st.warning("该年份暂无数据。")

# --- 功能 2: 会议关键词 ---
with tab2:
    st.subheader("2. 特定会议年度关键词分析")
    
    c1, c2 = st.columns(2)
    with c1:
        sel_conf = st.selectbox("选择会议", basic_info['conferences'])
    with c2:
        sel_year_conf = st.selectbox("选择年份", basic_info['years'], key="t2_year")
    
    kw_stats_conf, df_conf_scope = analyzer.get_keyword_stats(year=sel_year_conf, conference=sel_conf, limit=None)
    
    if not kw_stats_conf.empty:
        total_counts = kw_stats_conf['Count'].sum()
        kw_stats_conf['Percentage'] = (kw_stats_conf['Count'] / total_counts * 100).round(2)
        kw_stats_conf['Percentage_Str'] = kw_stats_conf['Percentage'].astype(str) + '%'

        st.write(f"**📊 {sel_conf} {sel_year_conf} Top 20 关键词排名**")
        fig_bar = px.bar(kw_stats_conf.head(20), x='Count', y='Keyword', orientation='h', 
                         color='Count', title=f'Top 20 Keywords in {sel_conf}', text='Count')
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("#### 🥧 关键词占比与详细数据")
        col_chart, col_table = st.columns([1, 1])
        with col_chart:
            st.write("**关键词占比分布**")
            fig_pie = px.pie(kw_stats_conf, values='Count', names='Keyword', 
                             hover_data=['Percentage'])
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_table:
            st.write("**全部关键词数据列表**")
            st.dataframe(
                kw_stats_conf[['Keyword', 'Count', 'Percentage_Str']], 
                column_config={
                    "Keyword": "关键词", "Count": st.column_config.NumberColumn("频次", format="%d"), "Percentage_Str": "占比"
                }, use_container_width=True, height=400
            )

        st.markdown("---")
        st.markdown("#### 🔎 论文反查")
        t_kw = st.selectbox(f"筛选 {sel_conf} 中的关键词:", kw_stats_conf['Keyword'].tolist(), key="t2_kw")
        if t_kw:
            papers = analyzer.get_papers_by_keyword_strict(t_kw, df_scope=df_conf_scope)
            st.write(f"找到 {len(papers)} 篇包含 **{t_kw}** 的论文：")
            for i, row in papers.iterrows():
                expander_title = f"📄 {row['title']}"
                with st.expander(expander_title):
                    st.markdown(f"**Title:** {row['title']}")
                    st.markdown(f"**👥 Authors:** {row['authors']}")
                    st.markdown(f"**🏷️ Keywords:** {row['keywords']}")
                    st.markdown("---")
                    st.markdown(f"**📝 Abstract:**")
                    st.write(row['abstract'])
    else:
        st.info("该筛选组合下无数据。")

# --- 功能 3: 关键词 -> 作者 ---
with tab3:
    st.subheader("3. 领域专家排位 (Who writes about X?)")
    sel_topic = st.selectbox("选择研究领域 (关键词)", all_unique_kws)
    if sel_topic:
        auth_stats, relevant_papers = analyzer.get_authors_by_keyword(sel_topic)
        if not auth_stats.empty:
            c_chart, c_list = st.columns([1, 1])
            with c_chart:
                st.write(f"**在 '{sel_topic}' 领域发文 Top 10**")
                fig = px.bar(auth_stats.head(10), x='Author', y='Paper_Count', 
                             color='Paper_Count', color_continuous_scale='Viridis')
                st.plotly_chart(fig, use_container_width=True)
            with c_list:
                st.write("**详细列表**")
                for idx, row in auth_stats.head(20).iterrows():
                    auth_name = row['Author']
                    p_list = relevant_papers[relevant_papers['authors'].str.contains(auth_name, regex=False)]
                    with st.expander(f"🏅 {idx+1}. {auth_name} ({row['Paper_Count']} 篇)"):
                        for _, p in p_list.iterrows():
                            st.markdown(f"**{p['title']}**")
                            st.info(f"📅 {p['year']} | 🏛️ {p['conference']} | 🏷️ {p['keywords']}")
                            st.markdown("---")

# --- 功能 4: 作者画像 (升级版) ---
with tab4:
    st.subheader("4. 作者投稿画像分析")
    
    all_authors = analyzer.get_all_authors_list()
    sel_author = st.selectbox("搜索作者", all_authors)
    
    if sel_author:
        # 获取基础数据
        auth_papers, conf_dist, year_trend = analyzer.get_author_profile(sel_author)
        # 获取详细关键词数据
        auth_kw_counts, auth_kw_trend = analyzer.get_author_keyword_details(auth_papers)
        
        st.success(f"👤 作者 **{sel_author}** 总计发表: {len(auth_papers)} 篇")
        
        # 1. 基础投稿统计 (会议 & 年份)
        st.markdown("### 📊 基础投稿分布")
        r1, r2 = st.columns(2)
        with r1:
            if not conf_dist.empty:
                fig_pie = px.pie(conf_dist, values='Count', names='Conference', hole=0.4, title="会议分布")
                st.plotly_chart(fig_pie, use_container_width=True)
        with r2:
            if not year_trend.empty:
                fig_line = px.line(year_trend, x='year', y='Count', markers=True, title="年度产出趋势")
                fig_line.update_yaxes(tick0=0, dtick=1)
                st.plotly_chart(fig_line, use_container_width=True)
        
        st.markdown("---")
        st.markdown("### 🧠 研究兴趣画像")
        
        # 2. 关键词画像 (柱状图 + 气泡图)
        if not auth_kw_counts.empty:
            c_kw_total, c_kw_trend = st.columns([1, 1.5])
            
            with c_kw_total:
                st.write("**🔬 核心研究兴趣 (Top 15 Keywords)**")
                # 柱状图使用 Keyword (大写)
                fig_kw_bar = px.bar(auth_kw_counts.head(15), x='Count', y='Keyword', orientation='h',
                                    color='Count', color_continuous_scale='Mint')
                fig_kw_bar.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_kw_bar, use_container_width=True)
                
            with c_kw_trend:
                st.write("**📅 研究兴趣演变 (Bubble Chart)**")
                
                top_kws = auth_kw_counts.head(15)['Keyword'].tolist()
                # 过滤
                filtered_trend = auth_kw_trend[auth_kw_trend['Keyword'].isin(top_kws)]
                
                if not filtered_trend.empty:
                    # === 修复点: 这里 y='Keyword' 必须是大写，与 analysis.py 对应 ===
                    fig_bubble = px.scatter(filtered_trend, x='year', y='Keyword', size='Count_Year',
                                            color='Count_Year', color_continuous_scale='Viridis',
                                            hover_data=['Count_Year'],
                                            title="研究热点随年份的变化")
                    
                    fig_bubble.update_yaxes(categoryorder='total ascending') 
                    fig_bubble.update_xaxes(type='category')
                    st.plotly_chart(fig_bubble, use_container_width=True)
                else:
                    st.info("数据量不足以生成演变图。")
        else:
            st.warning("该作者的论文未包含关键词数据。")
                
        st.markdown("---")
        st.markdown("### 📄 详细论文清单")
        for i, row in auth_papers.iterrows():
            label = f"[{row['year']}] [{row['conference']}] {row['title']}"
            with st.expander(label):
                st.markdown(f"**🏷️ Keywords:** {row['keywords']}")
                st.markdown(f"**👥 Authors:** {row['authors']}")
                st.markdown("**📝 Abstract:**")
                st.write(row['abstract'])

# --- 功能 5: 趋势分析 ---
with tab5:
    st.subheader("📈 关键词趋势演变分析")
    
    trend_type = st.radio("选择分析维度:", ["🌍 全局年度趋势 (所有会议)", "🏛️ 特定会议趋势"])
    
    if trend_type == "🌍 全局年度趋势 (所有会议)":
        st.markdown("### 全局 Top 20 关键词历年走势")
        trend_data = analyzer.get_keyword_trend_data(conference=None, top_n=20)
        if not trend_data.empty:
            fig_line = px.line(trend_data, x='year', y='Count', color='Keyword', markers=True,
                               title='Top 20 热门关键词历年频次变化')
            fig_line.update_layout(hovermode="x unified")
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("暂无足够数据生成趋势图。")
            
        st.markdown("### 📋 历年 Top 20 榜单对比")
        rank_matrix = analyzer.get_yearly_top_k_matrix(conference=None, k=20)
        st.dataframe(rank_matrix, use_container_width=True)
        
    else:
        sel_trend_conf = st.selectbox("选择会议进行趋势分析", basic_info['conferences'], key="t5_conf")
        st.markdown(f"### {sel_trend_conf} Top 20 关键词历年走势")
        
        trend_data_conf = analyzer.get_keyword_trend_data(conference=sel_trend_conf, top_n=20)
        if not trend_data_conf.empty:
            fig_line_conf = px.line(trend_data_conf, x='year', y='Count', color='Keyword', markers=True,
                                    title=f'{sel_trend_conf} Top 20 热门关键词频次变化')
            fig_line_conf.update_layout(hovermode="x unified")
            st.plotly_chart(fig_line_conf, use_container_width=True)
        else:
            st.info(f"{sel_trend_conf} 暂无足够数据。")
            
        st.markdown(f"### 📋 {sel_trend_conf} 历年 Top 20 榜单对比")
        rank_matrix_conf = analyzer.get_yearly_top_k_matrix(conference=sel_trend_conf, k=20)
        st.dataframe(rank_matrix_conf, use_container_width=True)