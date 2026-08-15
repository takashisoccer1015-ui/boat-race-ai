import streamlit as st
import pandas as pd
import numpy as np
import lightgbm as lgb

# ==========================================
# 0. ページ設定とタイトル
# ==========================================
st.set_page_config(page_title="AIボート予想システム", layout="wide")
st.title("🚤 独自AI ボートレース バリューベット抽出システム")
st.markdown("---")

# ==========================================
# 1. サイドバー（ユーザー入力パネル）
# ==========================================
st.sidebar.header("🎯 予測設定")

# 予算入力（ケリー基準の計算に使用）
bankroll = st.sidebar.number_input("1レースの予算 (円)", min_value=1000, value=10000, step=1000)

# 期待値の閾値（これ以上の買い目だけを表示）
threshold = st.sidebar.slider("期待値 (EV) の閾値", min_value=1.0, max_value=2.0, value=1.1, step=0.05)

# レース場とレース番号の選択（ダミー入力）
st.sidebar.markdown("---")
venue = st.sidebar.selectbox("レース場", ["戸田 (02)", "平和島 (04)", "多摩川 (05)"])
race_no = st.sidebar.selectbox("レース番号", [f"{i}R" for i in range(1, 13)])

if st.sidebar.button("AI予測を実行"):
    
    with st.spinner(f'{venue} {race_no} のデータを取得・解析中...'):
        # ==========================================
        # 2. 擬似的なデータパイプライン
        # ※実際はここに前述のスクレイピング＆推論コードが入ります
        # ==========================================
        import time
        time.sleep(1.5) # 処理してる感を出すためのウェイト
        
        # 擬似的なAI予測結果（全120通りの一部）
        combinations = ['1-2-3', '1-2-4', '1-3-2', '1-4-2', '2-1-3', '6-5-4', '3-1-4', '1-2-5', '4-1-2']
        ai_probs = [0.18, 0.12, 0.08, 0.06, 0.04, 0.002, 0.05, 0.07, 0.03]
        odds = [6.5, 8.5, 12.0, 15.0, 35.0, 450.0, 25.0, 11.0, 40.0]
        
        df = pd.DataFrame({
            '買い目': combinations,
            'AI予測勝率': ai_probs,
            '実際オッズ': odds
        })
        
        # ==========================================
        # 3. 期待値と推奨ベット額の計算
        # ==========================================
        df['期待値'] = df['AI予測勝率'] * df['実際オッズ']
        
        # ケリー基準
        df['b'] = df['実際オッズ'] - 1.0
        df['kelly'] = (df['AI予測勝率'] * (df['b'] + 1.0) - 1.0) / df['b']
        df['kelly'] = df['kelly'].clip(lower=0)
        
        # ベット額計算（100円単位切り捨て）
        df['推奨購入額'] = (df['kelly'] * bankroll // 100) * 100
        
        # 閾値以上を抽出してソート
        value_bets = df[df['期待値'] >= threshold].sort_values('期待値', ascending=False)
        
        # ==========================================
        # 4. 結果のWeb画面出力
        # ==========================================
        st.success("✅ 解析が完了しました！")
        
        if value_bets.empty:
            st.warning("⚠️ 指定した閾値（期待値）を超える美味しい買い目はありません。このレースは見送りを推奨します。")
        else:
            # 見た目を整えるためのカラム表示
            col1, col2, col3 = st.columns(3)
            col1.metric("ターゲットレース", f"{venue} {race_no}")
            col2.metric("総推奨投資額", f"¥{int(value_bets['推奨購入額'].sum()):,}")
            col3.metric("発見された買い目", f"{len(value_bets)} 点")
            
            st.markdown("### 🔥 バリューベット一覧")
            
            # DataFrameをスタイリングして表示（不要な列は隠す）
            display_df = value_bets[['買い目', 'AI予測勝率', '実際オッズ', '期待値', '推奨購入額']].copy()
            display_df['AI予測勝率'] = display_df['AI予測勝率'].apply(lambda x: f"{x*100:.1f}%")
            display_df['実際オッズ'] = display_df['実際オッズ'].apply(lambda x: f"{x:.1f}倍")
            display_df['期待値'] = display_df['期待値'].apply(lambda x: f"{x:.2f}")
            display_df['推奨購入額'] = display_df['推奨購入額'].apply(lambda x: f"¥{int(x):,}")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # オマケ：期待値の可視化グラフ
            st.markdown("### 📊 期待値分布グラフ")
            chart_data = value_bets[['買い目', '期待値']].set_index('買い目')
            st.bar_chart(chart_data)

else:
    st.info("👈 左のサイドバーから設定を行い、「AI予測を実行」ボタンを押してください。")
