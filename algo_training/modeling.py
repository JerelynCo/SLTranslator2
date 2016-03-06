#Essentials
import pandas as pd
import numpy as np
import string

#Preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.cross_validation import train_test_split

#Libraries for the estimators
from sklearn.decomposition import PCA
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import MultinomialNB
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis

#Utilities
from sklearn.cross_validation import cross_val_score, KFold
from scipy.stats import sem
from sklearn import metrics
from sklearn.grid_search import GridSearchCV

#Model persistence
from sklearn.externals import joblib

#Analysis
import seaborn as sb

def data_cleaning(file):
    feature_names = ['fPinky', 'fRing', 'fMiddle', 'fIndex', 'fThumb', 'c1', 'c2', 'c3', 'c4', 'aX', 'aY', 'aZ', 'gX', 'gY', 'gZ', 'label']
    a = pd.read_excel(file, convert_float=True, names=feature_names)
    a.dropna(how='any',inplace=True)
    a.to_csv(file.split(".")[0] + ".csv", index=False)

def plot_scatter(X_estimator, letter, title):
    plt.figure()
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(12, 8)
    for i in range(len(target_names)):
        px = X_estimator[y == i, 0]
        py = X_estimator[y == i, 1]
        if i is letter :
            plt.scatter(px, py, c='red', zorder=2)
        else:
            plt.scatter(px, py, c='silver', alpha=0.5, zorder=1)
        plt.legend(target_names)
        plt.title("PCA 2 Components plot for letter %s" % target_names[letter])
             
# data_cleaning("5.xlsx")

#Data Parameters
target_names = [i for i in string.ascii_uppercase]
target_names.extend(['_', '/', '-']) #Space, enter, rest/stop
feature_names = ['label','fPinky', 'fRing', 'fMiddle', 'fIndex', 'fThumb', 'c1', 'c2', 'c3', 'c4', 'aX', 'aY', 'aZ', 'gX', 'gY', 'gZ']

data = pd.concat([pd.read_csv("data/" + str(i)+".csv") for i in range(1,5)])
sl = data.sample(frac=0.33).reset_index(drop=True)
sl_data = sl.iloc[:,:-1]
sl_target = sl['label'].apply(lambda x: target_names.index(x)).values

#Extra evaluations
# sl.describe()
# sb.pairplot(sl.dropna(), hue='label')
# sl.loc[sl['label'] == 'A', 'fThumb'].hist()

X, y = sl_data, sl_target
#Standardize X because of different scaling from different sensors
X_std = StandardScaler().fit_transform(X) 

print("***** Data loaded and standardized *****")

def plotPCA():
	print("***** Plotting PCA *****")
	n = 15
	pca = PCA(n_components=n)
	X_pca = pca.fit(X_std).transform(X_std)
	for i in range(10):
	    plot_scatter(X_pca, i, "PCA of the dataset")

	print('Explained variance ratio (first %s components): %s' % (str(n), str(pca.explained_variance_ratio_)))


"""
Gesture Recognition thru Machine Learning

Machine learning algorithms applied to glove sensor values to derive the categories.

Includes the analysis of the following unsupervised algorithms:

    PCA

Includes the analysis of the following supervised algorithms:

    SVC
    K Neighbors Classifier
    Decision Tree Classifier
    Random Forest Classifier
    Ada Boost Classifier
    Gaussian Naive Bayes
    Linear Discrimninant Analysis
    Quadratic Discriminant Analysis
"""

X_train, X_test, y_train, y_test = train_test_split(X_std, y, test_size=0.25, random_state=0)


def evaluate_cross_validation(clf, K):
    # create a k-fold croos validation iterator
    cv = KFold(len(y_train), K, shuffle=True, random_state=0)
    # by default the score used is the one returned by score method of the estimator (accuracy)
    scores = cross_val_score(clf, X_train, y_train, cv=cv)
    print(scores)
    print(("Mean score: {0:.3f} (+/-{1:.3f})").format(np.mean(scores), sem(scores)))
    
def fit_clf(clf):
	clf.fit(X_train, y_train)
	return clf

def train_and_evaluate(clf):
    clf.fit(X_train, y_train)
    print("Accuracy on training set:")
    print(clf.score(X_train, y_train))
    print("Accuracy on testing set:")
    print(clf.score(X_test, y_test))
    y_pred = clf.predict(X_test)
    print("Classification Report:")
    print(metrics.classification_report(y_test, y_pred))
    print("Confusion Matrix:")
    print(metrics.confusion_matrix(y_test, y_pred))
    return clf

names = [
		"Nearest Neighbors", 
		"Linear SVM",
		"RBF SVM", 
		"Decision Tree",
        "Random Forest",
        "AdaBoost", 
        "Naive Bayes"
        # "Linear Discriminant Analysis",
        # "Quadratic Discriminant Analysis"
         ]
classifiers = [
    KNeighborsClassifier(),
    SVC(),
    SVC(),
    DecisionTreeClassifier(),
    RandomForestClassifier(),
    AdaBoostClassifier(),
    GaussianNB()
    # LinearDiscriminantAnalysis(),
    # QuadraticDiscriminantAnalysis()
    ]

parameters = [
	{'n_neighbors': [3, 5, 8, 12]},
	{'kernel': ['linear'], 'C': [1, 10, 100, 1000]},
	{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4, 2], 'C': [1, 10, 100, 1000, 1200]},
    {'max_depth': [3, 5, 8, 12, 20]},
    {'max_depth': [3, 5, 8, 12], 'n_estimators': [5, 10, 15], 'max_features': [1, 3, 5]},
    {'n_estimators': [30, 50, 100]},
    {},
]

print("***** Modeling start *****")

clf_predictor = []
for name, clf, parameter in zip(names, classifiers, parameters):
    print("\n################ %s ################" % name)
    grid_search = GridSearchCV(clf, parameter, cv = 5)
    grid_search.fit(X_train, y_train)

    print("Best parameters set found on development set: \n %s" % str(grid_search.best_params_))
    print("Grid scores on development set: \n")
    for params, mean_score, scores in grid_search.grid_scores_:
        print("%0.3f (+/-%0.03f) for %r"
              % (mean_score, scores.std() * 2, params))
    
    print("The model is trained on the full development set. \n The scores are computed on the full evaluation set. \n")
    y_true, y_pred = y_test, grid_search.predict(X_test)
    print(metrics.classification_report(y_true, y_pred))

    clf_predictor.append(grid_search)
    # evaluate_cross_validation(clf, K=5)
    # clf_predictor.append(fit_clf(clf))
    # clf_predictor.append(train_and_evaluate(clf, X_train, X_test, y_train, y_test))

