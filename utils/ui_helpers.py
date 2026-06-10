import base64
import streamlit as st


def get_base64_image(image_path):

    with open(image_path, "rb") as img_file:

        return base64.b64encode(
            img_file.read()
        ).decode()


def card(
    label,
    image_path,
    state_key,
    session_state,
    t,
    value=None
):

    compare_value = value if value else label

    selected = (
        session_state[state_key]
        == compare_value
    )

    background = (
        "#eef7fd"
        if selected
        else "white"
    )

    border = (
        "2px solid #003b7a"
        if selected
        else "1px solid #d9dde3"
    )

    image_base64 = get_base64_image(
        image_path
    )

    html = f"""
    <html>
    <style>
        .profile-category-card {{
            border-radius:0px;
            padding:10px;
            width:100%;
            text-align:center;
            height:170px;
            box-sizing:border-box;
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
            transition: all 0.15s ease;
            overflow:hidden;
        }}
        .profile-category-card-disabled {{
            opacity:0.45;
        }}
        .profile-category-card-image {{
            width:120px;
            height:120px;
            object-fit:contain;
            margin-bottom:8px;
            flex:0 0 auto;
        }}
        .profile-category-card-label {{
            font-size:17px;
            font-weight:700;
            color:#2d343c;
            text-align:center;
            line-height:1.25;
            overflow-wrap:normal;
            word-break:normal;
            hyphens:none;
        }}
        .profile-category-card-label-disabled {{
            color:#999999;
        }}
        @media (max-width: 260px) {{
            .profile-category-card {{
                padding:8px 6px;
                height:165px;
            }}
            .profile-category-card-image {{
                width:108px;
                height:108px;
                margin-bottom:6px;
            }}
            .profile-category-card-label {{
                font-size:15px;
                line-height:1.2;
            }}
        }}
        @media (max-width: 190px) {{
            .profile-category-card {{
                height:160px;
            }}
            .profile-category-card-image {{
                width:96px;
                height:96px;
            }}
            .profile-category-card-label {{
                font-size:14px;
                line-height:1.18;
            }}
        }}
    </style>
    <body style="
        margin:0;
        padding:0;
    ">
    <div class="profile-category-card" style="
        border:{border};
        background-color:{background};
    ">

        <img class="profile-category-card-image"
        src="data:image/png;base64,{image_base64}" />

        <div class="profile-category-card-label">
            {label}
        </div>

    </div>
    </body>
    </html>
    """

    st.components.v1.html(
        html,
        height=170
    )

    if st.button(
        t("select"),
        key=f"{state_key}_{label}",
        use_container_width=True
    ):

        session_state[state_key] = compare_value

        if (
            compare_value == "Cirkulære rør middelsvære"
            or
            compare_value == "Cirkulære rør svære"
        ):

            session_state["sides"] = "4"

        st.rerun()


def disabled_card(
    label,
    image_path
):

    image_base64 = get_base64_image(
        image_path
    )

    html = f"""
    <html>
    <style>
        .profile-category-card {{
            border-radius:0px;
            padding:10px;
            width:100%;
            text-align:center;
            height:170px;
            box-sizing:border-box;
            display:flex;
            flex-direction:column;
            justify-content:center;
            align-items:center;
            transition: all 0.15s ease;
            overflow:hidden;
        }}
        .profile-category-card-disabled {{
            opacity:0.45;
        }}
        .profile-category-card-image {{
            width:120px;
            height:120px;
            object-fit:contain;
            margin-bottom:8px;
            flex:0 0 auto;
        }}
        .profile-category-card-label {{
            font-size:17px;
            font-weight:700;
            color:#2d343c;
            text-align:center;
            line-height:1.25;
            overflow-wrap:normal;
            word-break:normal;
            hyphens:none;
        }}
        .profile-category-card-label-disabled {{
            color:#999999;
        }}
        @media (max-width: 260px) {{
            .profile-category-card {{
                padding:8px 6px;
                height:165px;
            }}
            .profile-category-card-image {{
                width:108px;
                height:108px;
                margin-bottom:6px;
            }}
            .profile-category-card-label {{
                font-size:15px;
                line-height:1.2;
            }}
        }}
        @media (max-width: 190px) {{
            .profile-category-card {{
                height:160px;
            }}
            .profile-category-card-image {{
                width:96px;
                height:96px;
            }}
            .profile-category-card-label {{
                font-size:14px;
                line-height:1.18;
            }}
        }}
    </style>
    <body style="
        margin:0;
        padding:0;
    ">
    <div class="profile-category-card profile-category-card-disabled" style="
        border:1px solid #d9dde3;
        background:white;
    ">

        <img class="profile-category-card-image"
        src="data:image/png;base64,{image_base64}" />

        <div class="profile-category-card-label profile-category-card-label-disabled">
            {label}
        </div>

    </div>
    </body>
    </html>
    """

    st.components.v1.html(
        html,
        height=170
    )
