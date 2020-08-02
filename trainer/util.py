from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os

import numpy as np
import pandas as pd
import tensorflow as tf

# Storage directory
DATA_DIR = os.path.join('data')

# Download options.
TRAINING_FILE = os.path.join(DATA_DIR, 'adult.data.csv')
EVAL_FILE = os.path.join(DATA_DIR, 'adult.test.csv')

# This is the label (target) we want to predict.
_LABEL_COLUMN = 'income_bracket'

UNUSED_COLUMNS = ['fnlwgt', 'education', 'gender']

_CATEGORICAL_COLUMNS = [
    'workclass', 'marital_status', 'occupation', 'relationship', 'race', 'native_country', 'income_bracket']


def preprocess(dataframe):
    """Converts categorical features to numeric. Removes unused columns.

    Args:
      dataframe: Pandas dataframe with raw data

    Returns:
      Dataframe with preprocessed data
    """
    dataframe = dataframe.drop(columns=UNUSED_COLUMNS)

    # Convert integer valued (numeric) columns to floating point
    numeric_columns = dataframe.select_dtypes(['int64']).columns
    dataframe[numeric_columns] = dataframe[numeric_columns].astype('float32')

    # Convert categorical columns to numeric
    cat_columns = dataframe.select_dtypes(['object']).columns
    vocabulary = {x: pd.api.types.CategoricalDtype(
        categories=dataframe[x].dropna().unique()) for x in _CATEGORICAL_COLUMNS}
    dataframe[cat_columns] = dataframe[cat_columns].apply(
        lambda x: x.astype(vocabulary[x.name]))
    dataframe[cat_columns] = dataframe[cat_columns].apply(
        lambda x: x.cat.codes)
    return dataframe


def standardize(dataframe):
    """Scales numerical columns using their means and standard deviation to get
    z-scores: the mean of each numerical column becomes 0, and the standard
    deviation becomes 1. This can help the model converge during training.

    Args:
      dataframe: Pandas dataframe

    Returns:
      Input dataframe with the numerical columns scaled to z-scores
    """
    dtypes = list(zip(dataframe.dtypes.index, map(str, dataframe.dtypes)))
    # Normalize numeric columns.
    for column, dtype in dtypes:
        if dtype == 'float32':
            dataframe[column] -= dataframe[column].mean()
            dataframe[column] /= dataframe[column].std()
    return dataframe


def load_data():
    """Loads data into preprocessed (train_x, train_y, eval_y, eval_y)
    dataframes.

    Returns:
      A tuple (train_x, train_y, eval_x, eval_y), where train_x and eval_x are
      Pandas dataframes with features for training and train_y and eval_y are
      numpy arrays with the corresponding labels.
    """

    # This census data uses the value '?' for missing entries. We use
    # na_values to
    # find ? and set it to NaN.
    # https://pandas.pydata.org/pandas-docs/stable/generated/pandas.read_csv
    # .html
    train_df = pd.read_csv(TRAINING_FILE, na_values='?')
    eval_df = pd.read_csv(EVAL_FILE, na_values='?')

    train_df = preprocess(train_df)
    eval_df = preprocess(eval_df)

    # Split train and eval data with labels. The pop method copies and removes
    # the label column from the dataframe.
    train_x, train_y = train_df, train_df.pop(_LABEL_COLUMN)
    eval_x, eval_y = eval_df, eval_df.pop(_LABEL_COLUMN)

    # Join train_x and eval_x to normalize on overall means and standard
    # deviations. Then separate them again.
    all_x = pd.concat([train_x, eval_x], keys=['train', 'eval'])
    all_x = standardize(all_x)
    train_x, eval_x = all_x.xs('train'), all_x.xs('eval')

    # Reshape label columns for use with tf.data.Dataset
    train_y = np.asarray(train_y).astype('float32').reshape((-1, 1))
    eval_y = np.asarray(eval_y).astype('float32').reshape((-1, 1))

    return train_x, train_y, eval_x, eval_y
