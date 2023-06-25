import datetime as dt
import pandas as pd
import numpy as np
import os
import sys
import re



def obtain_cols(df): 

    df["num_tumors"]=df.filter(regex="^n_tumor_").count(axis=1)
    df["num_tumors"].replace(0, np.nan, inplace=True)

    df['Age'] = np.nan
    df.loc[df['death_date'].notnull(), 'Age'] = (pd.to_datetime(df["death_date"]) - pd.to_datetime(df['birth_date'])).astype('timedelta64[Y]')
    df.loc[df['death_date'].isnull(), 'Age'] = (dt.datetime.today() - pd.to_datetime(df['birth_date'])).astype('timedelta64[Y]')
    df[["age_at_diagnosis", "Age"]] = df[["age_at_diagnosis", "Age"]].apply(pd.to_numeric, errors='coerce')
    conditions = [
        (df['menopause_pre'] == 1) | (df['Age'] >= 58),
        (df['menopause_pre'] == 0)
    ]
    choices = ['yes', 'no']
    default_choice = np.nan
    df['menopause'] = np.select(conditions, choices, default_choice)
    df["pregnancy"] = df["pregnancy"].where(df["pregnancy"] != 999, "one at least")

    df = df.replace("acetato de megestrol", "megesterol acetate", regex=True)
    
    df=df.rename(columns={'birth': 'natural_birth'})
    df["recurrence"] = np.where(df["recurrence_year"].notnull(), "yes", "no")
    df["death"] = np.where(df["death_date"].notnull(), "yes", "no")


        
    n_tumors = df.filter(regex="tumor_date_").shape[1]
    excluded_histological = []
    n_tumors=df.filter(regex="tumor_date_").shape[1]
    for i in range(1, n_tumors+1):
        if i+1 <= n_tumors: 
            # get the corresponding column name for each _number column
            lob_col = f'lobular_{i}'
            ductal_col = f'ductal_{i}'
            nos_col = f'nos_{i}'
            # create a new column with the histological type based on the conditions
            for idx, row in df.iterrows():
                if row[lob_col] == 1 and not row[ductal_col] == 1 and not row[nos_col] == 1:
                    df.at[idx, f'histological_type_{i}'] = 'Lobular'
                elif row[ductal_col] == 1 and not row[lob_col] == 1 and not row[nos_col] == 1:
                    df.at[idx, f'histological_type_{i}'] = 'Ductal'
                elif row[nos_col]== 1 and not row[ductal_col] == 1 and not row[lob_col] == 1:
                    df.at[idx, f'histological_type_{i}'] = 'No specific type'
                elif (row[nos_col] == 1 and row[ductal_col] == 1) or (row[nos_col] == 1 and row[lob_col] == 1) or (row[ductal_col] == 1 and row[lob_col] == 1):
                    df.at[idx, f'histological_type_{i}'] = "Exclude"
                    excluded_histological.append(row["ehr"])
                else: 
                    df.at[idx, f'histological_type_{i}'] = np.nan 



    excluded_behavior = []
    for i in range(1, n_tumors+1):
        if i+1 <= n_tumors: 
            # get the corresponding column name for each _number column
            invasive = f'invasive_{i}'
            in_situ = f'in_situ_{i}'
            
            # create a new column with the histological type based on the conditions
            for idx, row in df.iterrows():
                if row[invasive] == 1 and not row[in_situ] == 1:
                    df.at[idx, f'behavior_{i}'] = 'Invasive'
                elif row[in_situ] == 1 and not row[invasive] == 1:
                    df.at[idx, f'behavior_{i}'] = 'In situ'
                elif row[invasive] == 1 and row[in_situ] == 1:
                    df.at[idx, f'behavior_{i}'] =  "Exclude"
                    excluded_behavior.append(row["ehr"])
                else:
                    df.at[idx, f'behavior_{i}'] = np.nan


    for i in range(1, n_tumors+1):
        if i+1 <= n_tumors: 
            # get the corresponding column name for each _number column
            invasive = f'invasive_{i}'
            associated_insitu = f'associated_in_situ_{i}'
            in_situ = f'in_situ_{i}'
            # create a new column with the histological type based on the conditions
            for idx, row in df.iterrows():
                if row[invasive] == 1 and row[associated_insitu] == 1:
                    df.at[idx, f'associated_col_{i}'] = 'Associated in situ'
                elif row[invasive] == 1 and not row[associated_insitu] == 1:
                    df.at[idx, f'associated_col_{i}'] = 'No associated in situ'
                elif row[in_situ] == 1:
                    df.at[idx, f'associated_col_{i}'] =  "Exclude"
                else: 
                    df.at[idx, f'associated_col_{i}'] =  np.nan

    cols_to_summarize = [col for col in df.columns if re.match(r'stage_diagnosis_\d+', col)]
    #cols_to_summarize = [col for col in df.columns if 'stage_diagnosis_' in col]

    # create summary columns
    for col in cols_to_summarize:
        # extract number from column name
        num = col.split('_')[-1]
        # create summary column name
        summary_col = f'stage_diagnosis_summ_{num}'
        # create mapping dictionary for stage grouping
        mapping = {'IA': 'I', 'IB': 'I', 'IIA': 'II', 'IIB': 'II', 'IIC': 'II', 
                'IIIA': 'III', 'IIIB': 'III', 'IIIC': 'III', '0': '0', 'IV': 'IV'}
        # apply mapping to create summary column
        #df[summary_col] = df[col].map(mapping)
        df[summary_col] = np.where(df[col].astype(str).str.contains('x', na=False), 'Exclude', df[col].map(mapping))

    cols_to_summarize = [col for col in df.columns if re.match(r'stage_after_neo_\d+', col)]
    for col in cols_to_summarize:
        # extract number from column name
        num = col.split('_')[-1]
    
        # create summary column name
        summary_col = f'stage_after_neo_summ_{num}'
        # create mapping dictionary for stage grouping
        mapping = {'IA': 'I', 'IB': 'I', 'IIA': 'II', 'IIB': 'II', 'IIC': 'II', 
                'IIIA': 'III', 'IIIB': 'III', 'IIIC': 'III', '0': '0', 'IV': 'IV'}
        # apply mapping to create summary column
        #df[summary_col] = df[col].map(mapping)
        df[summary_col] = np.where(df[col].astype(str).str.contains('x', na=False), 'Exclude', df[col].map(mapping))



    excluded_histological = []
    for i in range(1, n_tumors+1):
        
            
            # get the corresponding column name for each _number column
        er_col = f'er_positive_{i}'
        pr_col = f'pr_positive_{i}'
        her2_col = f'her2_positive_{i}'
            # create a new column with the histological type based on the conditions
        for idx, row in df.iterrows():
            if row[er_col] == 1:
                df.at[idx, f'er_positive_cat_{i}'] = 'Yes'
            elif row[er_col] == 0:
                df.at[idx, f'er_positive_cat_{i}'] = 'No'
                
            else: 
                df.at[idx, f'er_positive_cat_{i}'] = np.nan 

            if row[pr_col] == 1:
            #and not row[lob_col] == 1 and not row[nos_col] == 1:
                df.at[idx, f'pr_positive_cat_{i}'] = 'Yes'
                    
            elif row[pr_col] == 0:
                df.at[idx, f'pr_positive_cat_{i}'] = 'No'
                
            else: 
                df.at[idx, f'pr_positive_cat_{i}'] = np.nan 

            if row[her2_col]== 1:
                #and not row[ductal_col] == 1 and not row[lob_col] == 1:
                df.at[idx, f'her2_positive_cat_{i}'] = 'Yes'
            elif row[her2_col] == 0:
                df.at[idx, f'her2_positive_cat_{i}'] = 'No'
                
            else: 
                df.at[idx, f'her2_positive_cat_{i}'] = np.nan


    df = df.replace("nan", np.nan)

                
    df["N_surgeries"] = df.filter(regex="surgery_\d+").count(axis=1)
    df["N_chemotherapies"] = df.filter(regex="qt_schema_\d+").count(axis=1)
    df["N_hormonetherapies"]=df.filter(regex="drug_\d+").count(axis=1)

    return df


def nearest(df, sdate, edate, regex):
    result = []
    result_name =[]
    date_columns = df.filter(regex=regex).columns
    for _, row in df.iterrows():
        tumor_date_1 = row[sdate]
        tumor_date_2 = row[edate] 
        if pd.isnull(tumor_date_1):
            result.append(np.nan)
            result_name.append(np.nan)
        else:
            eligible_cols = [col for col in date_columns if pd.notna(row[col]) and (pd.isnull(tumor_date_2) or row[col] < tumor_date_2) and (row[col] > tumor_date_1)]
            if not eligible_cols:
                result.append(np.nan)
                result_name.append(np.nan)
            else:
                nearest_col = min(eligible_cols, key=lambda col: row[col] - tumor_date_1)
                result.append((row[nearest_col]))
                result_name.append(nearest_col)
                            
    return result, result_name

def neo_stop(df, reference_col, limit_col=None):
    last_date_cols = [col for col in df.columns if col.startswith("last_date_schema_")]
    first_date_cols = [col.replace("last", "first") for col in last_date_cols[1:]]
    stop_names = []
    stop_dates = []

    for i, row in df.iterrows():
        stop_neo_name = np.nan
        stop_neo_date = np.nan
        earliest_col = None
        diff_days_list = []

        for col in last_date_cols:
            if limit_col is not None:
                #[col_first for col_first in first_date_cols if row[col] < row[col_first]]
                #(row[col] > row[reference_col]) and (pd.isnull(row[limit_col]) or row[col] < row[limit_col]):
                eligible_cols = [col_first for col_first in first_date_cols if (row[col] < row[col_first]) and (row[col] < row[limit_col] or pd.isnull(row[limit_col]))]
                
            else:
                eligible_cols = [col_first for col_first in first_date_cols if row[col] < row[col_first]]

            if eligible_cols:
                earliest_col = min(eligible_cols, key=lambda col_first: row[col_first] - row[col])

                if earliest_col is not None:
                    diff_days = (row[earliest_col] - row[col]).days
                else:
                    diff_days = np.nan

                diff_days_list.append(diff_days)

                if diff_days >= 20:
                    stop_neo_date = row[col]
                    stop_neo_name = str(col)
                    break

        stop_names.append(stop_neo_name)
        stop_dates.append(stop_neo_date)

    return stop_names, stop_dates



def next_dates(df, source_col, regex):
    date_cols = df.filter(regex=regex).columns
    result = pd.Series(index=df.index, dtype='datetime64[ns]')
    for i, row in df.iterrows():
        result[i] = min([row[col] for col in date_cols if pd.notna(row[col]) and row[col] > row[source_col]], default=np.nan)
    return result

def to_date(df): 
    date_columns = ["death_date", "diagnosis_date"]
    #date_columns += [col for col in df.columns if col.startswith("neoadjuvant_")]
    date_columns += [col for col in df.columns if col.startswith("tumor_date_")]
    date_columns += [col for col in df.columns if col.startswith("surgery_date_")]
    date_columns += [col for col in df.columns if col.startswith("first_date_schema_")]
    date_columns += [col for col in df.columns if col.startswith("last_date_schema_")]


    for col in date_columns:
        if col.startswith("surgery_date_day_"):
            # For surgery date columns, combine year, month, and day columns to create a datetime column
            surgery_num = col.split("_")[3]
            surgery_date_col = "surgery_date_" + surgery_num
            surgery_year_col = "surgery_date_year_" + surgery_num
            surgery_month_col = "surgery_date_month_" + surgery_num
            surgery_day_col = "surgery_date_day_" + surgery_num


            df[surgery_date_col] = pd.to_datetime({
                "year": df[surgery_year_col],
                "month": df[surgery_month_col],
                "day": df[surgery_day_col]
            }, errors="coerce")
        else:
            df[col] = pd.to_datetime(df[col])

    # Get the correct diagnosis date for each tumor
    tumor_columns = [col for col in df.columns if col.startswith("tumor_date_")]
    for tumor_col in tumor_columns:
        tumor_num = tumor_col.split("_")[2]
        tumor_date_col = "tumor_date_" + tumor_num
        tumor_date = df[tumor_date_col]
        tumor_1_date = df["tumor_date_1"]
        diagnosis_date = df["diagnosis_date"]
        # If the difference between tumor 1 date and diagnosis date is greater than 1 year or tumor 1 date is null,
        # use the diagnosis date as the tumor date
        if ((tumor_1_date.isnull()) | ((tumor_1_date - diagnosis_date).dt.days > 365)).all():
            df[tumor_date_col] = diagnosis_date
    
    
    # Convert first and last schema dates to datetime format
    first_schema_columns = [col for col in df.columns if col.startswith("first_date_schema_")]
    last_schema_columns = [col for col in df.columns if col.startswith("last_date_schema_")]
    for schema_col in first_schema_columns + last_schema_columns:
        df[schema_col] = pd.to_datetime(df[schema_col])
    return df



def extract_intervals_3000(df): 
    
    df["Time_to_recurrence_months"] = (df["recurrence_year"] - df["diagnosis_date"].dt.year)*12
    df["Time_to_death_months"] = ((df["death_date"] - df["diagnosis_date"])).dt.days//30


    n_tumors=df.filter(regex="tumor_date_").shape[1]
    for i in range(1, n_tumors+1):
        if all(col in df.columns for col in ["tumor_date_"+str(i), "neoadjuvant_"+str(i)]):
            if "tumor_date_"+str(i+1) in df.columns: 
                tumor_date_col = 'tumor_date_' + str(i)
                tumor_date_lim = 'tumor_date_' + str(i+1)
                neoadjuvant_col = 'neoadjuvant_' + str(i)
                col_name_1 = "first_treatment_date_" + str(i)
                col_name_2="first_treatment_name_"+ str(i)
                df[col_name_1] = np.where(df[neoadjuvant_col] == 'yes', 
                            nearest(df, tumor_date_col, tumor_date_lim, "^first_date_schema_\d+$")[0], 
                            nearest(df, tumor_date_col, tumor_date_lim, "^surgery_date_\d+$")[0])
                df[col_name_2] = np.where(df[neoadjuvant_col] == 'yes', 
                            nearest(df, tumor_date_col, tumor_date_lim, "^first_date_schema_\d+$")[1], 
                            nearest(df, tumor_date_col, tumor_date_lim, "^surgery_date_\d+$")[1])
            else:
                tumor_date_col = 'tumor_date_' + str(i)
                #tumor_date_lim = 'tumor_date_' + str(i+1)
                neoadjuvant_col = 'neoadjuvant_' + str(i)
                col_name_1 = "first_treatment_date_" + str(i)
                col_name_2="first_treatment_name_"+ str(i)
                df[col_name_1] = np.where(df[neoadjuvant_col] == 'yes', 
                            next_dates(df, tumor_date_col, regex="^first_date_schema_\d+$")[0], 
                            next_dates(df, tumor_date_col, regex="^surgery_date_\d+$")[0])
                df[col_name_2] = np.where(df[neoadjuvant_col] == 'yes', 
                            next_dates(df, tumor_date_col,  regex="^first_date_schema_\d+$")[1], 
                            next_dates(df, tumor_date_col,  regex="^surgery_date_\d+$")[1]) 

    for i in range(1, n_tumors+1):
        if all(col in df.columns for col in ["tumor_date_"+str(i), "first_treatment_date_"+str(i)]):
        
        #if ("tumor_date_"+str(i)) and ("first_treatment_date_"+str(i)) in df.columns: 
            tumor_date_col = 'tumor_date_' + str(i)
            first_treatment_col = "first_treatment_date_"+str(i)
            df["Time_dx_first_treatment_"+str(i)] = (pd.to_datetime(df[first_treatment_col])-pd.to_datetime(df[tumor_date_col])).dt.days
   


    for i in range(1, n_tumors+1):
        if all(col in df.columns for col in ["tumor_date_"+str(i), "neoadjuvant_"+str(i), "first_treatment_date_"+str(i)]):
            if "tumor_date_"+str(i+1) in df.columns: 
        #if ("tumor_date_"+str(i+1)) and ("first_treatment_date_"+str(i)) and ("neoadjuvant_"+str(i)) in df.columns: 
                neoadjuvant_col = 'neoadjuvant_' + str(i)
                col_name_1 = "Time_dx_surgery_no_neo_days_" + str(i)
            
                df[col_name_1] = np.where( (df[neoadjuvant_col] == 'no') & (df["first_treatment_name_"+str(i)].astype(str).str.contains("surgery")), 
                            df["Time_dx_first_treatment_"+str(i)], 
                            np.nan)
    
    return df



def extract_intervals_2025(df): 
    
    df["Time_to_recurrence_months"] = (df["recurrence_year"] - df["diagnosis_date"].dt.year)*12
    df["Time_to_death_months"] = ((df["death_date"] - df["diagnosis_date"])).dt.days//30


    n_tumors=df.filter(regex="tumor_date_").shape[1]
    for i in range(1, n_tumors+1):
        if all(col in df.columns for col in ["tumor_date_"+str(i), "neoadjuvant_"+str(i)]):
            if "tumor_date_"+str(i+1) in df.columns: 
                tumor_date_col = 'tumor_date_' + str(i)
                tumor_date_lim = 'tumor_date_' + str(i+1)
                neoadjuvant_col = 'neoadjuvant_' + str(i)
                col_name_1 = "first_treatment_date_" + str(i)
                col_name_2="first_treatment_name_"+ str(i)
                df[col_name_1] = np.where(df[neoadjuvant_col] == 'yes', 
                            nearest(df, tumor_date_col, tumor_date_lim, "^first_date_schema_\d+$")[0], 
                            nearest(df, tumor_date_col, tumor_date_lim, "^surgery_date_\d+$")[0])
                df[col_name_2] = np.where(df[neoadjuvant_col] == 'yes', 
                            nearest(df, tumor_date_col, tumor_date_lim, "^first_date_schema_\d+$")[1], 
                            nearest(df, tumor_date_col, tumor_date_lim, "^surgery_date_\d+$")[1])
            else:
                tumor_date_col = 'tumor_date_' + str(i)
                #tumor_date_lim = 'tumor_date_' + str(i+1)
                neoadjuvant_col = 'neoadjuvant_' + str(i)
                col_name_1 = "first_treatment_date_" + str(i)
                col_name_2="first_treatment_name_"+ str(i)
                df[col_name_1] = np.where(df[neoadjuvant_col] == 'yes', 
                            next_dates(df, tumor_date_col, regex="^first_date_schema_\d+$")[0], 
                            next_dates(df, tumor_date_col, regex="^surgery_date_\d+$")[0])
                df[col_name_2] = np.where(df[neoadjuvant_col] == 'yes', 
                            next_dates(df, tumor_date_col,  regex="^first_date_schema_\d+$")[1], 
                            next_dates(df, tumor_date_col,  regex="^surgery_date_\d+$")[1]) 

    for i in range(1, n_tumors+1):
        if all(col in df.columns for col in ["tumor_date_"+str(i), "first_treatment_date_"+str(i)]):
        
        #if ("tumor_date_"+str(i)) and ("first_treatment_date_"+str(i)) in df.columns: 
            tumor_date_col = 'tumor_date_' + str(i)
            first_treatment_col = "first_treatment_date_"+str(i)
            df["Time_dx_first_treatment_"+str(i)] = (pd.to_datetime(df[first_treatment_col])-pd.to_datetime(df[tumor_date_col])).dt.days
   


    for i in range(1, n_tumors+1):
        if all(col in df.columns for col in ["tumor_date_"+str(i), "neoadjuvant_"+str(i), "first_treatment_date_"+str(i)]):
            if "tumor_date_"+str(i+1) in df.columns: 
        #if ("tumor_date_"+str(i+1)) and ("first_treatment_date_"+str(i)) and ("neoadjuvant_"+str(i)) in df.columns: 
                neoadjuvant_col = 'neoadjuvant_' + str(i)
                col_name_1 = "Time_dx_surgery_no_neo_days_" + str(i)
            
                df[col_name_1] = np.where( (df[neoadjuvant_col] == 'no') & (df["first_treatment_name_"+str(i)].astype(str).str.contains("surgery")), 
                            df["Time_dx_first_treatment_"+str(i)], 
                            np.nan)
                
    for i in range (1, n_tumors+1): 
        if "Time_dx_first_treatment_"+str(i) in df.columns: 
            df["Time_dx_neo_days_"+str(i)] = np.where(df["neoadjuvant_"+str(i)] == "yes", df["Time_dx_first_treatment_"+str(i)], np.nan)
        
       

        for i in range (1, n_tumors+1): 

            for i in range(1, n_tumors+1):
                if all(col in df.columns for col in ["tumor_date_"+str(i)]):
                    if "tumor_date_"+str(i+1) in df.columns: 
                        df["neo_stop_date_"+str(i)] = neo_stop(df, "tumor_date_"+str(i), "tumor_date_"+str(i+1))[1]
                        
                    else: 
                       
                        df["neo_stop_date_"+str(i)] = neo_stop(df, "tumor_date_"+str(i))[1]
        
        for i in range(1, n_tumors+1):
            if all(col in df.columns for col in ["tumor_date_"+str(i), "neo_stop_date_"+str(i)]):
                if "tumor_date_"+str(i+1) in df.columns:
                     
                    tumor_date_lim = 'tumor_date_' + str(i+1)
                    neoadjuvant_col = 'neoadjuvant_' + str(i)
                    col_name_1 = "surgery_after_neo_date_" + str(i)
                  

                    df[col_name_1] = nearest(df, "neo_stop_date_"+str(i), tumor_date_lim, "^surgery_date_\d+$")[0]


        for i in range(1, n_tumors+1): 
           if "surgery_after_neo_date_"+str(i) in df.columns: 
               df["Time_neo_next_surgery_days_"+str(i)] = np.where(df["neoadjuvant_"+str(i)] == "yes", 
                                                                (pd.to_datetime(df["surgery_after_neo_date_"+ str(i)]) - pd.to_datetime(df["neo_stop_date_"+str(i)])).dt.days, 
                                                               np.nan)

    return df



def create_treatment_columns(df, regex_pattern):
      
    # Select columns that match the regex pattern
    selected_columns = [col for col in df.columns if re.search(regex_pattern, col)]

    # Get unique categories in selected columns
    unique_categories = set()
    for col in selected_columns:
        unique_categories.update(df[col].dropna().astype(str).unique())

    # Create new columns for each unique category with words separated by underscores
    new_columns = list(unique_categories)
    # Create a new DataFrame to store the results
    df_res = pd.DataFrame(0, index=df.index, columns=new_columns)

    # Iterate over each row
    for col in selected_columns:
        for category in unique_categories:
            mask = df[col].astype(str).str.contains(category)
            df_res.loc[mask, category] = 1

    # Drop columns with regex pattern "surgery_[0-9]"
    # df = df.drop(columns=selected_columns)
    df= pd.concat([df, df_res], axis=1)

    return df

def any_treatments(df): 
    neo_cols = df.filter(regex=("neoadjuvant_\d+")).columns.to_list()
    drug_columns = df.filter(regex=("drug_")).columns.to_list()
    surgery_columns = df.filter(regex=("surgery_\d+")).columns.to_list()
    schema_columns = df.filter(regex=("qt_schema_\d+")).columns.to_list()
    df["Any_surgery"]=np.where(df[surgery_columns].isnull().all(1), "no", "yes")
    df["Any_radiotherapy"]=np.where(df["n_radio"].isnull(), "no", "yes")
    df["Any_neo"] = np.where((df[neo_cols] == "yes").any(1), "yes", "no")
    df["Any_hormonetherapy"] =np.where(df[drug_columns].isnull().all(1), "no", "yes")
    df["Any_chemotherapy"] =np.where(df[schema_columns].isnull().all(1), "no", "yes")
    return df


#df= create_treatment_columns(df, r'surgery_[0-9]+')
#df = create_treatment_columns(df, r'drug_[0-9]+')
#df = df.drop(columns=[col for col in df.columns if '_date' in col and col != "diagnosis_date"])


def col_select_3000(df): 
    df_selection = df[[
    'age_at_diagnosis',
    'anastrozole',
    'fulvestrant',
    'capecitabine',
    'tamoxifen',
    'megestrol acetate',
    'abemaciclib',
    'everolimus',
    'vinorelbine',
    'palbociclib',
    'goserelin',
    'exemestane',
    'olaparib',
    'letrozole',
    'alpelisib',
    'ribociclib', 
    'partial mastectomy',
    'sentinel lymph node biopsy',
    'lymphadenectomy',
    'mastectomy',
    'menarche_age',
    'pregnancy',
    'abort',
    'natural_birth',
    'caesarean',
    'behavior_1',
    'histological_type_1',
    'associated_col_1',
    'grade_1',
    'ki67_1',
    'neoadjuvant_1',
    'type_1',
    'autoimmune disease',
    'cardiac insufficiency',
    'diabetes',
    'dislipemia',
    'ex-smoker',
    'gastrointestinal disease',
    'hta',
    'insomnia',
    'ischemic cardiopathology',
    'liver disease',
    'lung disease',
    'musculoskeletal disease',
    'other cardiopathology',
    'psychiatric disorder',
    'renal disease',
    'smoker',
    'thyroid disease',
    'transplant',
    'menopause',
    'Time_to_recurrence_months',
    'recurrence',
    'Time_dx_surgery_no_neo_days_1',
    'stage_diagnosis_summ_1',
    'stage_after_neo_summ_1',
     
    "her2_positive_cat_1", "er_positive_cat_1", "pr_positive_cat_1", 'Any_surgery',
    'Any_radiotherapy',
    'Any_hormonetherapy']]

    df_selection[["abort", "pregnancy", "caesarean", 
                  "natural_birth", "N_surgeries", 
                  "N_hormonetherapies", "n_radio", "grade_1"]] = df[["abort", "pregnancy",  "caesarean", "natural_birth", "N_surgeries", "N_hormonetherapies", "n_radio", "grade_1"]].astype("category")
    columns_to_replace = ['anastrozole', 'fulvestrant', 'capecitabine', 'tamoxifen', 'megestrol acetate', 'abemaciclib',
                      'everolimus', 'vinorelbine', 'palbociclib', 'goserelin', 'exemestane', 'olaparib', 'letrozole',
                      'alpelisib', 'ribociclib', 'partial mastectomy', 'sentinel lymph node biopsy', 'lymphadenectomy', "mastectomy"]

    df_selection[columns_to_replace] = df_selection[columns_to_replace].replace({0: 'no', 1: 'yes'})

   




    return df_selection

def col_select_2025(df): 
    df_selection = df[['ehr',
    'birth_date',
    'diagnosis_date',
    'age_at_diagnosis',
    'death_date',
    'age_at_death',
    
    'partial mastectomy',
    'sentinel lymph node biopsy',
    'lymphadenectomy',
    'mastectomy',
    'recurrence_year',
    'menarche_age',
    'pregnancy',
    'abort',
    'natural_birth',
    'caesarean',
    'behavior_1',
    'histological_type_1',
    'associated_col_1',
    'grade_1',
    'ki67_1',
    'neoadjuvant_1',
    'type_1',
    'autoimmune disease',
    'cardiac insufficiency',
    'diabetes',
    'dislipemia',
    'ex-smoker',
    'gastrointestinal disease',
    'hta',
    'insomnia',
    'ischemic cardiopathology',
    'liver disease',
    'lung disease',
    'musculoskeletal disease',
    'other cardiopathology',
    'psychiatric disorder',
    'renal disease',
    'smoker',
    'thyroid disease',
    'transplant',
    'menopause',
    'Time_to_recurrence_months',
    'recurrence',
    'Time_dx_surgery_no_neo_days_1',
    'Time_dx_neo_days_1',
    "time_from_neo_to_next_surgery_days_1", 
    'stage_diagnosis_summ_1',
    'stage_after_neo_summ_1',
    'num_tumors', 
    "her2_positive_cat_1", 
    "er_positive_cat_1", "pr_positive_cat_1", 'Any_surgery',
    'Any_radiotherapy',
    'Any_hormonetherapy', "N_surgeries", "N_hormonetherapies", "n_radio", 
    'PACLITAXEL + CARBOPLATINO',
 'TRASTUZUMAB + DOCETAXEL + PERTUZUMAB',
 'DOCETAXEL + CICLOFOSFAMIDA',
 'EPIRUBICINA + CICLOFOSFAMIDA + FLUOROURACILO',
 'TRASTUZUMAB + PERTUZUMAB',
 'DOCETAXEL + CARBOPLATINO',
 'CARBOPLATINO',
 'GEMCITABINA + PM060184',
 'PACLITAXEL + DEXAMETASONA',
 'CAELYX',
 'EPIRUBICINA + FLUOROURACILO',
 'TRASTUZUMAB + CAPECITABINA',
 'PACLITAXEL + AVASTIN',
 'TRASTUZUMAB + PACLITAXEL + DOXORRUBICINA + PERTUZUMAB',
 'UTEFOS',
 'DOCETAXEL + DOXORRUBICINA',
 'TRASTUZUMAB + PACLITAXEL + PERTUZUMAB',
 'CICLOFOSFAMIDA',
 'TRASTUZUMAB + PERTUZUMAB + CAPECITABINA',
 'FLUOROURACILO',
 'TRASTUZUMAB + PACLITAXEL',
 'DOCETAXEL + PERTUZUMAB',
 'CAPECITABINA',
 'TRASTUZUMAB + CARBOPLATINO + PERTUZUMAB',
 'TRASTUZUMAB',
 'ETOPOSIDO',
 'PACLITAXEL',
 'DOCETAXEL + CICLOFOSFAMIDA + DOXORRUBICINA',
 'TRASTUZUMAB + CICLOFOSFAMIDA + FLUOROURACILO + PERTUZUMAB + EPIRUBICINA',
 'PACLITAXEL + DOCETAXEL',
 'DEXAMETASONA',
 'CISPLATINO',
 'ETOPOSIDO + CARBOPLATINO',
 'DEPOCYTE + AVASTIN',
 'NIVOLUMAB',
 'AVASTIN',
 'DEPOCYTE',
 'BEVACIZUMAB',
 'ERIBULINA',
 'PACLITAXEL + PERTUZUMAB',
 'UTEFOS + CISPLATINO',
 'DOCETAXEL + DEXAMETASONA',
 'ATEZOLIZUMAB + PACLITAXEL',
 'NAB-PACLITAXEL',
 'CICLOFOSFAMIDA + DOXORRUBICINA + FLUOROURACILO',
 'METOTREXATO + ERIBULINA',
 'TRASTUZUMAB + PACLITAXEL + CARBOPLATINO',
 'BLEOMICINA + ETOPOSIDO + CISPLATINO',
 'ETOPOSIDO + CISPLATINO',
 'PACLITAXEL + DOCETAXEL + PERTUZUMAB',
 'TRASTUZUMAB + DOCETAXEL + CARBOPLATINO',
 'PACLITAXEL + BEVACIZUMAB',
 'BLEOMICINA + VINCRISTINA',
 'GEMCITABINA + CARBOPLATINO',
 'DOCETAXEL',
 'GEMCITABINA',
 'CARBOPLATINO + PERTUZUMAB',
 'TRASTUZUMAB + DOCETAXEL + DEXAMETASONA + CARBOPLATINO',
 'NIVOLUMAB + BMS-986178',
 'PERTUZUMAB',
 'DOXORRUBICINA',
 'BMS-986178',
 'EPIRUBICINA + CICLOFOSFAMIDA',
 'ATEZOLIZUMAB',
 'TRASTUZUMAB + CARBOPLATINO',
 'CICLOFOSFAMIDA + DOXORRUBICINA', 'anastrozole',
    'fulvestrant',
    'capecitabine',
    'tamoxifen',
    'abemaciclib',
    'everolimus',
    'vinorelbine',
    'palbociclib',
   'goserelin',
   'exemestane',
   'olaparib',
   'letrozole',
   'alpelisib',
   'ribociclib']]

    df_selection[["abort", "pregnancy", "caesarean", 
                  "natural_birth", "N_surgeries", 
                  "N_hormonetherapies", "n_radio", 
                  "grade_1"]] = df[["abort", "pregnancy",  "caesarean", "natural_birth", 
                                                                    "N_surgeries", "N_hormonetherapies", "n_radio", 
                                                                    "grade_1"]].astype("category")
    columns_to_replace = ['partial mastectomy', 'sentinel lymph node biopsy', 'lymphadenectomy', "mastectomy", 'PACLITAXEL + CARBOPLATINO','TRASTUZUMAB + DOCETAXEL + PERTUZUMAB',
                        'DOCETAXEL + CICLOFOSFAMIDA', 'EPIRUBICINA + CICLOFOSFAMIDA + FLUOROURACILO','TRASTUZUMAB + PERTUZUMAB','DOCETAXEL + CARBOPLATINO','CARBOPLATINO',
                        'GEMCITABINA + PM060184','PACLITAXEL + DEXAMETASONA','CAELYX','EPIRUBICINA + FLUOROURACILO',
                        'TRASTUZUMAB + CAPECITABINA','PACLITAXEL + AVASTIN',
                        'TRASTUZUMAB + PACLITAXEL + DOXORRUBICINA + PERTUZUMAB','UTEFOS','DOCETAXEL + DOXORRUBICINA',
                        'TRASTUZUMAB + PACLITAXEL + PERTUZUMAB', 'CICLOFOSFAMIDA','TRASTUZUMAB + PERTUZUMAB + CAPECITABINA',
                          'FLUOROURACILO','TRASTUZUMAB + PACLITAXEL','DOCETAXEL + PERTUZUMAB','CAPECITABINA',
                          'TRASTUZUMAB + CARBOPLATINO + PERTUZUMAB','TRASTUZUMAB','ETOPOSIDO','PACLITAXEL','DOCETAXEL + CICLOFOSFAMIDA + DOXORRUBICINA',
 'TRASTUZUMAB + CICLOFOSFAMIDA + FLUOROURACILO + PERTUZUMAB + EPIRUBICINA',
 'PACLITAXEL + DOCETAXEL', 'anastrozole',
    'fulvestrant',
    'capecitabine',
    'tamoxifen',
    'abemaciclib',
    'everolimus',
    'vinorelbine',
    'palbociclib',
   'goserelin',
   'exemestane',
   'olaparib',
   'letrozole',
   'alpelisib',
   'ribociclib', 
 'DEXAMETASONA',
 'CISPLATINO',
 'ETOPOSIDO + CARBOPLATINO',
 'DEPOCYTE + AVASTIN',
 'NIVOLUMAB',
 'AVASTIN',
 'DEPOCYTE',
 'BEVACIZUMAB',
 'ERIBULINA',
 'PACLITAXEL + PERTUZUMAB',
 'UTEFOS + CISPLATINO',
 'DOCETAXEL + DEXAMETASONA',
 'ATEZOLIZUMAB + PACLITAXEL',
 'NAB-PACLITAXEL',
 'CICLOFOSFAMIDA + DOXORRUBICINA + FLUOROURACILO',
 'METOTREXATO + ERIBULINA',
 'TRASTUZUMAB + PACLITAXEL + CARBOPLATINO',
 'BLEOMICINA + ETOPOSIDO + CISPLATINO',
 'ETOPOSIDO + CISPLATINO',
 'PACLITAXEL + DOCETAXEL + PERTUZUMAB',
 'TRASTUZUMAB + DOCETAXEL + CARBOPLATINO',
 'PACLITAXEL + BEVACIZUMAB',
 'BLEOMICINA + VINCRISTINA',
 'GEMCITABINA + CARBOPLATINO',
 'DOCETAXEL',
 'GEMCITABINA',
 'CARBOPLATINO + PERTUZUMAB',
 'TRASTUZUMAB + DOCETAXEL + DEXAMETASONA + CARBOPLATINO',
 'NIVOLUMAB + BMS-986178',
 'PERTUZUMAB',
 'DOXORRUBICINA',
 'BMS-986178',
 'EPIRUBICINA + CICLOFOSFAMIDA',
 'ATEZOLIZUMAB',
 'TRASTUZUMAB + CARBOPLATINO',
 'CICLOFOSFAMIDA + DOXORRUBICINA']

    df_selection[columns_to_replace] = df_selection[columns_to_replace].replace({0: 'no', 1: 'yes'})


#'anastrozole', 'fulvestrant', 'capecitabine', 'tamoxifen', 'megestrol acetate', 'abemaciclib',
 #                     'everolimus', 'vinorelbine', 'palbociclib', 'goserelin', 'exemestane', 'olaparib', 'letrozole',
 #                     'alpelisib', 'ribociclib',










    return df_selection