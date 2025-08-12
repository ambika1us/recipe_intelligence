import os
import urllib.parse
import pandas as pd
from sqlalchemy import create_engine, text
import streamlit as st
from dotenv import load_dotenv
import re

# -------------------
# Load Environment Variables (Neon)
# -------------------
load_dotenv()
DATABASE_URL = os.getenv("NEON_DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

st.title("🍲 Ingredient Intelligence — Neon-Enabled")

# -------------------
# Cached DB Query Function
# -------------------
@st.cache_data(ttl=300)
def get_data(query, params=None):
    try:
        with engine.connect() as connection:
            stmt = text(query)
            df = pd.read_sql_query(stmt, connection, params=params)
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

# -------------------
# Cuisine Selection
# -------------------
data_cuisine = "SELECT DISTINCT cuisine FROM ingredients ORDER BY cuisine"
df_cuisine = get_data(data_cuisine)
if df_cuisine.empty:
    st.error("No cuisines loaded.")
    st.stop()

sel_cui = st.selectbox("Select a Cuisine", df_cuisine['cuisine'])
query = """
    SELECT final_ingredients AS ingredients 
    FROM ingredients
    WHERE cuisine = :cui
"""
df = get_data(query, params={'cui': sel_cui})

# -------------------
# Ingredients Multiselect
# -------------------
user_opt = st.multiselect("Select Available Ingredients", sorted(df['ingredients'].tolist()))
if not user_opt:
    st.warning("Please select at least one ingredient.")
    st.stop()

# -------------------
# Full-Text Search for Recipes
# -------------------
search_terms = ' | '.join([re.sub(r'\s+', ' & ', ing.strip()) for ing in user_opt])

query = """
    SELECT recipe_name, ingredients, total_time_mins,
       ts_rank(to_tsvector('english', cleaned), websearch_to_tsquery(:search_terms)) AS rank
              FROM recipes
                     WHERE to_tsvector('english', cleaned) @@ websearch_to_tsquery(:search_terms)
                            ORDER BY rank DESC, total_time_mins ASC
                                   LIMIT 10

"""
recipes_df = get_data(query, params={'search_terms': search_terms})

if recipes_df.empty:
    st.warning("No matching recipes found.")
    st.stop()

# -------------------
# Cooking Time Filter
# -------------------
valid_times = recipes_df["total_time_mins"].dropna()
valid_times = valid_times[valid_times > 0]
if valid_times.empty:
    st.warning("No cookable recipes with positive time found.")
    st.stop()

min_time = int(valid_times.min())
max_time = int(valid_times.max())

# set defaults
min_val = min_time
max_val = max_time

# adjust if they are equal
if min_time == max_time:
    min_val = min_time - 1
    max_val = max_time + 1

min_selected, max_selected = st.slider(
    "Cooking Time Range (minutes)",
    min_val,
    max_val,
    (min_val, max_val)
)

filtered_df = recipes_df[
    (recipes_df["total_time_mins"] >= min_selected) &
    (recipes_df["total_time_mins"] <= max_selected)
]

quick_recipes = filtered_df.sort_values("total_time_mins").head(10)
st.subheader("⏱️ Recipes Under Your Time Limit:")
st.dataframe(quick_recipes[["recipe_name", "total_time_mins"]], use_container_width=True)

# -------------------
# Fetch Instructions
# -------------------
if not quick_recipes.empty:
    recipe_names = quick_recipes["recipe_name"].tolist()
    placeholders = ', '.join([f":name{i}" for i in range(len(recipe_names))])

    query = f"""
        SELECT rname, instructions
        FROM instructions
        WHERE rname IN ({placeholders})
    """
    params = {f"name{i}": name for i, name in enumerate(recipe_names)}
    instructions_df = get_data(query, params=params)
else:
    instructions_df = pd.DataFrame()

instructions_df["instructions"] = instructions_df["instructions"].fillna("").astype(str)
merged_df = pd.merge(
    instructions_df,
    quick_recipes,
    left_on="rname",
    right_on="recipe_name",
    how="inner"
)

# -------------------
# Step-by-Step Renderer with Ingredient Highlight
# -------------------
def render_ordered_instructions(text, ingredients):
    if not isinstance(text, str):
        return "<p><em>No instructions available.</em></p>"

    steps = re.split(r'(?<=[.!?]) +', text)
    steps = [step.strip() for step in steps if step.strip()]
    for i, step in enumerate(steps):
        for ing in sorted(ingredients, key=len, reverse=True):
            step = re.sub(rf'(?i)\b{re.escape(ing)}\b', f"<strong>{ing}</strong>", step)
        steps[i] = step
    ol_html = "<ol>" + "".join(f"<li>{step}</li>" for step in steps) + "</ol>"
    return ol_html

for _, row in merged_df.iterrows():
    with st.expander(f"📖 {row['rname']} ({row['total_time_mins']} mins)"):
        st.markdown(f"**{row['rname']} — {row['total_time_mins']} minutes**")
        st.markdown(render_ordered_instructions(row['instructions'], user_opt), unsafe_allow_html=True)
