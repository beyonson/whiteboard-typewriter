clear
clc
close

%% Import image
img = imread('s.png');
img = img(:,:,1);

% img = imresize(img, 20, 'nearest');
img = imresize(img, 20);
% imshow(img)

%% Skeletonization
img_log = imbinarize(imcomplement(img));
imshow(img_log)
img_skel = bwskel(img_log, 'MinBranchLength', 500);

% img = (imcomplement(img));
% imshow(img)
% img_skel = edge(img,'canny');
% 
%% GHT

imshow(img_skel);

