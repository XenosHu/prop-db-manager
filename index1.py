import streamlit as st
import insert_build
import insert_unit
import search
import sql_test
import manage
import hmac

def main():
    st.title("房源数据管理")
    st.sidebar.title("目录")
    choice = st.sidebar.selectbox("选择", ["添加公寓", "添加单元", "搜索房源", "测试"])

    if choice == "添加公寓":
        insert_build.app()
    elif choice == "添加单元":
        insert_unit.app()
    elif choice == "搜索房源":
        search.app()
    elif choice == "测试":
        sql_test.app()

if __name__ == "__main__":
    main()
