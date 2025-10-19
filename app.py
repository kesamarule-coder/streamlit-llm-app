from dotenv import load_dotenv

load_dotenv()


# --- import: 標準→サードパーティ→自作 ---

import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks import BaseCallbackHandler

load_dotenv()  # .envの読み込み（1回で十分）

# --- コーチングスタイルごとのプロンプト定義 ---
EXPERT_MAP = {
    "A (戦場の鏡)": "あなたは厳しいコーチです。現状の思考を破壊し、抽象度の高いGoal設定を強制的に促してください。",
    "B (温かな光源)": "あなたは共感的なコーチです。自己効力感の強化と小さな成功体験の積み重ねを重視し、持続的な成長をサポートしてください。"
}

# --- Streamlitストリーミング出力ハンドラー ---
class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text, unsafe_allow_html=True)

def get_llm_response(input_text: str, expert_type: str) -> str | None:
    """
    入力テキストと専門家タイプを受け取り、LLMからの回答をストリーミングで画面に出力する。
    """
    system_prompt = EXPERT_MAP.get(expert_type)
    if not system_prompt:
        st.error("エラー: 無効な専門家タイプが選択されました。")
        return None
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input_text}")
    ])
    llm = ChatOpenAI(
        model="gpt-3.5-turbo-0125",
        temperature=0.0,
        streaming=True
    )
    chain = prompt | llm
    response_container = st.empty()
    handler = StreamHandler(response_container)
    try:
        response = chain.invoke(
            {"input_text": input_text},
            config={"callbacks": [handler]}
        )
        return response.content
    except Exception as e:
        st.error(f"LLM呼び出し中にエラーが発生しました: {e}")
        return None

# --- この下に他のブロックが続きます ---
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        # markdown=TrueでリアルタイムにMarkdownを解釈
        self.container.markdown(self.text, unsafe_allow_html=True)

# ----------------------------------------------------
# メイン処理関数 (要件に合わせた定義)
# ----------------------------------------------------
def get_llm_response(input_text: str, expert_type: str):
    """
    入力テキストと専門家タイプを受け取り、LLMからの回答をストリーミングで画面に出力する。
    """
    
    # 1. 選択されたプロンプトを取得
    system_prompt = EXPERT_MAP.get(expert_type)
    
    if not system_prompt:
        st.error("エラー: 無効な専門家タイプが選択されました。")
        return

    # 2. プロンプトテンプレートの定義
    # システムメッセージ内の {input_text} プレースホルダーに、ユーザー入力を渡す
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input_text}")
    ])
    
    # 3. LLMの初期化
    # APIキーは環境変数から自動で読み込まれます
    # ストリーミングのために temperature=0 を推奨（回答の揺らぎを減らす）
    llm = ChatOpenAI(
        model="gpt-3.5-turbo-0125", 
        temperature=0.0,
        streaming=True # ストリーミングを有効化
    )
    
    # 4. Chainの実行とストリーミング出力
    chain = prompt | llm

    # Streamlitコンテナを作成し、ハンドラーに渡す
    response_container = st.empty()
    handler = StreamHandler(response_container)

    # 実行。callbacksにハンドラーを指定することで、トークン生成ごとに画面に出力される
    # LangChainの Lesson8 を参考にストリーミング処理を実装
    response = chain.invoke(
        {"input_text": input_text},
        config={"callbacks": [handler]}
    )
    
    # 最終的な回答内容を戻り値として返す (今回はストリーミングをメインにするため、ここでは実質不要だが、要件に合わせてresponse.contentを返す)
    return response.content

# ----------------------------------------------------
# ブロック 4, 5 のコードがこの下に続きます
# ----------------------------------------------------

# app.py (ブロック3の get_llm_response 関数の定義の後に追記)

# ----------------------------------------------------
# ブロック 4: Streamlit UIの構築と統合（メイン処理）
# ----------------------------------------------------

def main():
    # ページ設定: タイトルとワイドレイアウト
    st.set_page_config(page_title="認知科学コーチングAI", layout="wide")
    
    st.title("🧠 認知科学コーチングAI")
    
    # 4.1 UIの定義: 概要テキスト（要件）
    st.markdown("""
    ## 💡 Webアプリ概要と操作方法
    このアプリケーションは、あなたのGoal設定や課題に対し、【認知科学】に基づいた専門的なコーチングを提供します。
    以下のラジオボタンで、ご自身の課題フェーズに合ったコーチングスタイルを選択してください。
    
    - **A (戦場の鏡):** 厳しい指導で、現状の思考を破壊し、抽象度の高いGoal設定を強制的に促します。
    - **B (温かな光源):** 共感と自己効力感の強化に焦点を当て、小さな成功体験を積み重ねる持続的な成長をサポートします。
    """)
    
    st.markdown("---")
    
    # 4.1 UIの定義: 専門家の選択（ラジオボタン）
    expert_choice = st.radio(
        "**1. コーチングスタイルを選択してください:**",
        options=list(EXPERT_MAP.keys()),
        index=0, # 初期値は厳しいコーチ (A)
        horizontal=True
    )
    
    # 4.1 UIの定義: 入力フォーム
    user_input = st.text_area(
        "**2. 相談内容、または設定したいGoal案を入力してください:**",
        placeholder="例：どうしても朝起きられず、タスクが山積しています。解決したいです。",
        height=180
    )
    
    # 4.2 実行ロジックの実装 (ボタンを押した時)
    if st.button("🚀 コーチに相談（回答を取得）"):
        if user_input:
            # 処理中のUI表示
            with st.spinner(f"**{expert_choice}** があなたの内部モデルを分析中です..."):
                try:
                    # 回答表示用のプレースホルダーを作成し、ストリーミングを開始
                    st.markdown("---")
                    st.markdown(f"### 🤖 **{expert_choice}** からのフィードバック")
                    
                    # ブロック3で定義した関数を呼び出し（ストリーミング出力）
                    # get_llm_responseは内部でストリーミング処理を行う
                    get_llm_response(user_input, expert_choice)
                    
                except Exception as e:
                    st.error("エラーが発生しました。APIキーまたはネットワーク接続を確認してください。")
                    # デバッグ用: st.error(f"詳細エラー: {e}")
        else:
            st.warning("相談内容を入力フォームに入力してください。")

# アプリケーションのエントリーポイント
if __name__ == "__main__":
    # st.write("デバッグ: アプリケーション開始") # デバッグ時はコメントを外す
    main()