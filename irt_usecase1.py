
from math import sqrt
from math import exp
import random

# create a list of 801 zeros which we will fill later
# This is an array of theta (z-scores) from -4.0 to +4.0 at decimal place to 0.01, so there are 801 values [-4.000, -3.999, … 3.999, 4.000].  
# This is the array that will be used to calculate the likelihood of the examinee’s response vector for each theta value.
# The theta_array is used to calculate the likelihood of the examinee’s response vector for each theta value.

theta_array = [0] * 800
p_array = [0] * 800
scored_p_array = [0] * 800

# create a 801 element list ranging from -4.0 to 4.0   Note that Python is zero-referenced index

for i in range(800):
    theta_array[i] = -4.0 + (i * 0.01)
print(theta_array)


def item_response_function(theta_array, irt_a, irt_b, irt_c, scored_response_vector):
    
    # create a list with random values of 1 and 0 of length 40

    #scored_response_vector =  random.choices([0, 1], k=40)
    print(scored_response_vector)
    number_items = len(scored_response_vector)

    # Initialize LikeArray and BayesArray for this examinee
    sigma = 1.0  # double, this is a constant
    mu = 0.0  # double, this is a constant


    like_array = [1] * 800
    bayes_array = [exp(-((theta_array[column] - mu) * (theta_array[column] - mu) / (2 * sigma))) / sqrt(2 * 3.141529 * sigma) for column in range(800)]

    # print(bayes_array)
    
    # Determine if NonMixed = true

    non_mixed = False  # default
    raw_score = sum(scored_response_vector)

    if raw_score == 0 or raw_score == number_items:
        non_mixed = True
        max_like_column = 0  # default value for non_mixed case
    else:
        max_like_column = None

    # Calculate the LikeArray and BayesArray
    print("number of items: ", number_items)  # for QA
    for item in range(0, number_items):
        
        print("Item: ",item,"   Response", scored_response_vector[item])  # for QA
        for theta_column in range(0, 800):
            # print(irt_c[item])

            p = irt_c[item] + (1-irt_c[item]) * ((exp(1.702 * irt_a[item] * (theta_array[theta_column] - irt_b[item]))) / (1 + exp(1.702 * irt_a[item] * (theta_array[theta_column] - irt_b[item]))))
            p_array[theta_column] = p
            #like_array[theta_column] *= p
            scored_p_array[theta_column] = p
            if scored_response_vector[item] == 0:
                scored_p_array[theta_column] = 1-p  # turn into Q
            like_array[theta_column] *= scored_p_array[theta_column]
            bayes_array[theta_column] *= scored_p_array[theta_column]

       
        #print(p_array)  # for QA
        #print(scored_p_array)  # for QA

    # Find the value of Theta which has the highest likelihood (MaxLike)
    print(theta_array)  # for QA
    print(like_array)  # for QA
    max_like = 0

    for theta_column in range(0, 800):
        
        if not non_mixed:
            if like_array[theta_column] > max_like:
                max_like = like_array[theta_column]
                max_like_column = theta_column
            else:
                if bayes_array[theta_column] > max_like:
                    max_like = bayes_array[theta_column]
                    max_like_column = theta_column
        else:
            if bayes_array[theta_column] > max_like:
                max_like = bayes_array[theta_column]
                max_like_column = max_like_column  # use default value for non_mixed case


    current_theta = max_like_column / 100 - 4.01  # Finds theta value from -4 to +4
    print("Max like column", max_like_column)
    print("Current Theta: ", current_theta)
    return current_theta


def compute_english_scaled_score():
    
    """
    :return: english_scaled_score
    """
    scored_response_vector = [0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1]
    irt_a = [0.5943,0.3597,0.4506,0.4134,0.5523,0.747,0.5029,0.5079,0.5643,0.603,0.6443,0.5517,0.4547,0.4633,0.424,0.4539,0.4381,0.6347,0.403,0.4592,0.5772,0.5264,0.432,0.5277,0.4907,0.4441,0.6658,0.3951,0.4904,0.6835,0.5647,0.5446,0.5736,1.0,0.6044,0.5735,0.5169,0.485,0.3878,0.4272,0.6387,0.503,0.4916,1.0,0.594,0.6604,0.4875,0.4205,0.6641,0.6723,0.42,0.4229,0.3022,0.5551]
    irt_b = [1.8708,0.9149,0.9534,1.5535,-1.7252,-1.7091,-1.5754,-1.7725,-0.0647,-2.6507,0.4158,-2.3248,2.8864,-1.795,-2.5618,0.131,0.5972,-2.722,1.6051,-1.435,-2.9301,-3.2242,-2.2508,-0.6632,-1.3365,-1.4797,-3.691,0.1822,-0.4289,-4.0,-2.8589,-2.4616,-1.3176,-3.0,-1.4366,-1.9744,0.176,0.9291,-0.1185,-0.4021,-4.0,-3.1602,-2.1087,-3.0,-1.8509,-2.8799,-2.7475,0.5714,-2.9374,-4.0,-2.0957,-1.3104,-0.0465,-2.6331]
    irt_c = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    print(scored_response_vector)
    print("English Raw Score", sum(scored_response_vector))
    current_theta = item_response_function(theta_array, irt_a, irt_b, irt_c, scored_response_vector)
    print("English Theta: ", current_theta)
    english_scaled_score = current_theta * 33.3 + 641.875
    
    print(english_scaled_score)
    return english_scaled_score, sum(scored_response_vector)

def compute_math_scaled_score():
    
    """
    :return: math_scaled_score
    """
    scored_response_vector = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0]
    print(scored_response_vector)
    print("Math Raw Score", sum(scored_response_vector))
    irt_a = [0.3395,0.385,0.6299,0.6424,0.8205,0.8845,0.7828,0.9543,0.7773,0.7104,0.9001,0.7758,0.9032,0.8528,0.6552,0.9087,0.7219,0.6518,0.8732,0.8553,0.8689,0.715,0.8338,0.8869,1.0,1.0,0.8786,0.6109,0.8477,1.0654,0.8346,0.6739,0.854,0.8921,1.0752,1.0017,0.8239,0.5085,0.8652,0.7522,1.0411,0.6773,0.8627,0.5399]
    irt_b = [-4.0,-2.1109,-3.8775,-2.5362,-2.0675,-3.0073,-2.4523,-2.3717,-2.011,-1.7295,-1.155,-2.8897,2.5324,-1.9325,-1.3164,-2.78,-2.3635,-2.8149,-0.6723,-0.9468,-1.7561,-1.0775,-3.1791,-1.7489,-3.0,-3.0,-3.3443,-1.6131,-2.4871,-2.6246,-1.299,-0.4488,-1.8623,-2.5074,-1.2416,-0.6497,-1.8708,-1.1748,-1.9107,-0.108,-2.2692,-1.9098,-2.2934,-0.4943]
    irt_c = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    current_theta = item_response_function(theta_array, irt_a, irt_b, irt_c, scored_response_vector)
    math_scaled_score = current_theta * 35.672 + 699.468
    print("Math Theta: ", current_theta)
    print(math_scaled_score)
    
    return math_scaled_score, sum(scored_response_vector)

def section_switcher(theta):
    
    """
    here the theta value is used to determine the section
    for section switch the theta value is used to determine the section
    
    => 22 question scored_response_vector for english
    => 27 question scored_response_vector for math
    
    :return: section
    """
    if theta < 0:
        section = "B"
    elif theta >= 0:
        section = "C"
    return section

english, eraw = compute_english_scaled_score()
math, mraw = compute_math_scaled_score()
print("English Raw Score", eraw)
print("Math Raw Score", mraw)
print("English Score", english)
print("Math Score", math)
print("Combined SAT Score", english + math)