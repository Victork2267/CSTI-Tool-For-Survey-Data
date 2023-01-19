## Import modules
import numpy as np
import pandas as pd
import math
from scipy.stats import chi2_contingency

import streamlit as st

## User-Defined Functions

### Round up function
def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier

### Main ztable function
def create_ztable(df, group_differences, tar_question, T2T, T2B):

  ## Split dataframes
  df_group_diff = df[group_differences]
  df_tar_question = df[tar_question]

  ## Get table row labels
  row_label_list = [] 

  ### Append total
  row_label_list.append("Total")

  ## Append T2T and T2B
  row_label_list.append("T2T")
  row_label_list.append("T2B")

  for option in df_tar_question.value_counts().index.tolist():
    row_label_list.append(str(option))
  
  ## Get table col labels
  col_label_list = []

  ### Append total
  col_label_list.append("Total")

  for col in df_group_diff.value_counts().index.tolist():
    col_label_list.append(str(col))

  ## Values to host list values
  col_values_list = []

  ## Append values by creating column lists
  for i in col_label_list:
    temp_list = []

    if i == "Total":

      ## create a loop over the row variables
      for r in row_label_list:
        if r == "Total":
          val_r = len(df)
          val_r = "N=" + str(val_r)
          temp_list.append(val_r)
        else:
          val_r = np.round(len(df[df[tar_question] == str(r)])/len(df), 3)*100
          val_r = str(val_r) + "%"
          temp_list.append(val_r)
      
      col_values_list.append(temp_list)

    else:
      
      ## create a loop over the row variables
      for r in row_label_list:
        if r == "Total":
          val_r = len(df[df[group_differences] == str(i)])
          val_r = "N=" + str(val_r)
          temp_list.append(val_r)
        elif r == "T2T":
          try:
            val_r = np.round(len(df[(((df[tar_question] == str(T2T[0]))) | (df[tar_question] == str(T2T[1]))) & (df[group_differences] == str(i))])/len(df[df[group_differences] == str(i)]), 3)*100
            val_r = str(val_r) + "%"
            temp_list.append(val_r)
          except:
            temp_list.append("0.0%")
        elif r == "T2B":
          try:
            val_r = np.round(len(df[(((df[tar_question] == str(T2B[0]))) | (df[tar_question] == str(T2B[1]))) & (df[group_differences] == str(i))])/len(df[df[group_differences] == str(i)]), 3)*100
            val_r = str(val_r) + "%"
            temp_list.append(val_r)
          except:
            temp_list.append("0.0%")
        else:
          try:
            val_r = np.round(len(df[(df[tar_question] == str(r)) & (df[group_differences] == str(i))])/len(df[df[group_differences] == str(i)]), 3)*100
            val_r = str(val_r) + "%"
            temp_list.append(val_r)
          except:
            temp_list.append(val_r)
      
      col_values_list.append(temp_list)
  
  ## Create Z-table
  ztable_dict = {}
  
  ### Loop through col and generated lists
  for col, li in zip(col_label_list, col_values_list):
    ztable_dict[col] = li

  ## Create dataframe
  df_z = pd.DataFrame(ztable_dict)

  ## Label index
  print(row_label_list)
  df_z.index = row_label_list

  ## create contingency table
  ct = pd.crosstab(df[tar_question], df[group_differences], margins=True)
  res = chi2_contingency(np.array(ct))
  
  test_statistic = res[0]
  pvalue = res[1]
  dof = res[2]

  ## Set alpha to 0.05
  alpha = 0.05
  if pvalue <= alpha:
    conclusion = f"With a 95% confidence level, there is a dependent relationship between the variables; {tar_question}, and {group_differences}"
  else:
    conclusion = f"With a 95% confidence level, there is a independent relationship between the variables; {tar_question}, and {group_differences}"

  cstt = {"Test Statistic": [test_statistic], "P-value": [pvalue], "Degrees of Freedom": [dof], "Alpha": [alpha], "Conclusion": [conclusion]}

  df_cstt = pd.DataFrame(cstt)
  df_cstt.index = ["Results"]

  return df_z, df_cstt

## Main App
if __name__ == "__main__":
    st.title("Chi-Square Test of Independence Tool for Likert-scale Type Survey Data")

    source_file = st.file_uploader("To begin, Upload your source file *This source file should be an excel file")

    ### Check if a file has been uploaded
    if source_file is not None:

        st.info("File recieved -  Loading the Source File Now")
        
        ## load the file into a dataframe
        df = pd.read_excel(source_file)
        st.write("Dataset Loaded")
        st.dataframe(df)

        ## Load the options to select for main function
        st.subheader("Select the variables you want to examine")
        col1, col2 = st.columns(2)

        list_option = df.columns.tolist()

        with col1:
            group_diff = st.selectbox("Select the group difference", list_option)
        
        with col2:
            question = st.selectbox("Select the question", list_option)

        st.subheader("Select the top 2 and bottom 2 options")

        col11, col12 = st.columns(2)
        with col11:
            T2T_un = st.multiselect("Select the top 2 options", df[question].value_counts().index.tolist())
        
        with col12:
            T2B_un = st.multiselect("Select the bottom 2 options", df[question].value_counts().index.tolist())

        if st.button("Generate Table and Chi-Square Result"):
            
            ## Create table
            z_table, chi_table = create_ztable(df=df, group_differences=group_diff, tar_question=question, T2T=T2T_un, T2B=T2B_un)

            ## Analysis Table
            st.write("Analysis Table")
            st.dataframe(z_table)

            @st.cache
            def convert_df(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv().encode('utf-8')

            csv = convert_df(z_table)

            st.download_button(
                label="Download z-table",
                data=csv,
                file_name='z-table.csv',
                mime='text/csv',
            )

            ## Chi Square Table
            st.write("Chi-Square Table")
            st.dataframe(chi_table)

            @st.cache
            def convert_df(df):
                # IMPORTANT: Cache the conversion to prevent computation on every rerun
                return df.to_csv().encode('utf-8')

            csv = convert_df(chi_table)

            st.download_button(
                label="Download chi-square results",
                data=csv,
                file_name='chi-square-results.csv',
                mime='text/csv',
            )