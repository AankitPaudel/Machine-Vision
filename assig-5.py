# Ankit Paudel
import cv2
import numpy as np
import os

# Function to load images from specified file paths
def load_images(master_path, image1_path, image2_path):
    # Define paths to the images
    master_path = 'C:\\Users\\paude\\OneDrive\\Desktop\\Ankitnew\\CS445\\Assignment-5\\images\\master.jpg'
    image1_path = 'C:\\Users\\paude\\OneDrive\\Desktop\\Ankitnew\\CS445\\Assignment-5\\images\\varied_position.jpg'
    image2_path = 'C:\\Users\\paude\\OneDrive\\Desktop\\Ankitnew\\CS445\\Assignment-5\\images\\different_environment.jpg'

    # Read images using OpenCV
    master = cv2.imread(master_path)
    image1 = cv2.imread(image1_path)
    image2 = cv2.imread(image2_path)
    return master, image1, image2

# Function to detect features in an image using a specified method
def detect_features(image, method):
    # Choose the detector based on the method specified
    if method == "SIFT":
        detector = cv2.SIFT_create()
    elif method == "BRISK":
        detector = cv2.BRISK_create()
    elif method == "ORB":
        detector = cv2.ORB_create()
    else:
        raise ValueError(f"Unknown feature detection method: {method}")

    # Detect keypoints and compute descriptors
    keypoints, descriptors = detector.detectAndCompute(image, None)
    return keypoints, descriptors

# Function to match features between two sets of descriptors using the specified method
def match_features(desc1, desc2, method):
    # Choose the matcher based on the method specified
    if method == "BF":
        # Use Brute Force Matcher
        matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=False)
    elif method == "FLANN":
        # Use FLANN-based matcher with different settings based on descriptor type
        if desc1.dtype.type == np.float32:
            # Parameters for SIFT descriptors (float32)
            index_params = dict(algorithm=1, trees=10)
            search_params = dict(checks=100)
        else:
            # Parameters for binary descriptors like BRISK or ORB
            index_params = dict(algorithm=6, table_number=6, key_size=12, multi_probe_level=1)
            search_params = dict(checks=50)
        matcher = cv2.FlannBasedMatcher(index_params, search_params)
    
    # Perform knn matching 
    matches = matcher.knnMatch(desc1, desc2, k=2)
    good_matches = []
    # Apply Lowe's ratio test 
    for m_n in matches:
        if len(m_n) == 2:  # Ensure there are at least two 
            m, n = m_n
            if m.distance < 0.75 * n.distance:  # Lowe's ratio test
                good_matches.append(m)
    # Sort matches by their distance for better visualization
    return sorted(good_matches, key=lambda x: x.distance)

# Function to draw matches and save the output image
def draw_matches(master, image, kp1, kp2, matches, output_folder, feature_method, match_method, img_name):

    # Draw the top 10 matches between keypoints of master and current image
    result = cv2.drawMatches(master, kp1, image, kp2, matches[:10], None, flags=2)
    # Generate output filename based on feature and match methods
    output_filename = f"{feature_method}_{match_method}_{img_name}.png"
    # Save the resulting image in the specified output folder
    cv2.imwrite(os.path.join(output_folder, output_filename), result)

# Ensure the output directory exists, create it if not
output_folder = "output_images"
os.makedirs(output_folder, exist_ok=True)

# Load images from specified paths
master_image, image1, image2 = load_images('master.jpg', 'image1.jpg', 'image2.jpg')

# List of feature detection methods to use
feature_methods = ['SIFT', 'BRISK', 'ORB']
# List of matching methods to use
matching_methods = ['BF', 'FLANN']

# Iterate over each feature detection method
for feature_method in feature_methods:
    # Detect features for the master image
    master_kp, master_desc = detect_features(master_image, feature_method)
    # Iterate over the two other images 
    for image, img_name in [(image1, "image1"), (image2, "image2")]:
        # Detect features for the current image
        kp, desc = detect_features(image, feature_method)
        # matching method for the current feature detection method
        for match_method in matching_methods:
            # Match features between the master and current image descriptors
            matches = match_features(master_desc, desc, match_method)
            # Draw the matches and save the output image
            draw_matches(master_image, image, master_kp, kp, matches, output_folder, feature_method, match_method, img_name)

# Print message after all output files are saved
print("All output files have been saved successfully.")
