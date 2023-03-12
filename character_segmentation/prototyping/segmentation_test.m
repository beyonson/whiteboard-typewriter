clear
clc
close

%% Import image
img = imread('L.png');
img = img(:,:,1);

img = imresize(img, 20);

%% Skeletonization
img_log = imbinarize(imcomplement(img));
img_skel = bwskel(img_log);

%% GHT - Lines
[H, theta, rho] = hough_lines_acc(img_skel);
% fig = imshow(imadjust(rescale(H)));
% xlabel('\theta'), ylabel('\rho');

peaks = hough_peaks(H, 10, 'Threshold', 0.25 * max(H(:)), 'NHoodSize', [50 50]);  % defined in hough_peaks.m

%% Draw lines

fig = imshow(img);
hold on

line_cell = cell(size(peaks,1), 1);

for i = 1:size(peaks)
    cur_theta = theta(peaks(i,2));
    cur_rho = rho(peaks(i,1));

    if cur_theta == 0
        x1 = cur_rho;
        x2 = cur_rho;
        y1 = 1;
        y2 = size(img_skel,1);
    else
        x1 = 1;
        x2 = size(img_skel,2);
        y1 = (-cosd(cur_theta)/sind(cur_theta)) + (cur_rho/sind(cur_theta));
        y2 = (-cosd(cur_theta)/sind(cur_theta))*length(img_skel) + (cur_rho/sind(cur_theta));
    end

    xunit = linspace(x1, x2, max(abs(x2-x1)+1, abs(y2-y1)+1))';
    yunit = linspace(y1, y2, max(abs(x2-x1)+1, abs(y2-y1)+1))';


    line_cell{i,1} = [xunit, yunit];

    h = plot(xunit, yunit, 'Color', 'green', 'LineWidth', 5);

%     line([x1 x2], [y1 y2], 'Color', 'green', 'LineWidth', 5);

end

%% GHT - Circles

[centers, radii, votes] = find_circles(img_skel, [20:1:400], 0.6, 50);

centers = centers(votes > (0.5*max(votes)), :);
radii = radii(votes > (0.5*max(votes)) );

circle_cell = cell(size(centers,1), 3);

%% Draw Circles
th = 0:1:360;
for i = 1:size(centers,1)
    xunit = radii(i) * cosd(th) + centers(i,1);
    yunit = radii(i) * sind(th) + centers(i,2);

    circle_cell{i,1} = [xunit', yunit'];
    circle_cell{i,2} = radii(i);
    circle_cell{i,3} = centers(i,1);
    circle_cell{i,4} = centers(i,2);


    h = plot(xunit, yunit, 'Color', 'yellow', 'LineWidth', 5);
end

%% Get rid of circles that do not touch lines
for i = 1:size(circle_cell,1)

    touches_line = 0;
    cur_circle = circle_cell{i,1};

    for j = 1:size(line_cell,1)
        cur_line = line_cell{j,1};
        
        for ii = 1:size(cur_circle,1)

            if ((any(cur_line(:,1) >= cur_circle(ii,1) - 5) && any(cur_line(:,1) <= cur_circle(ii,1) + 5)) && ...
                    (any(cur_line(:,2) >= cur_circle(ii,2) - 5) && any(cur_line(:,2) <= cur_circle(ii,2) + 5)))
                touches_line = 1;
            end
        end
    end

    if (touches_line == 0)
        circle_cell{i,1} = [];
        circle_cell{i,2} = [];
        circle_cell{i,3} = [];
        circle_cell{i,4} = [];
    end
end

row_has_empty = any(cellfun(@isempty, circle_cell), 2);
circle_cell(row_has_empty,:) = [];

%% Draw Circles
th = 0:1:360;
for i = 1:size(circle_cell,1)
    h = plot(circle_cell{i,1}(:,1), circle_cell{i,1}(:,2), 'Color', 'green', 'LineWidth', 5);
end



[edge_row, edge_col] = find(img_skel==1);

th = 0:1:360;
for i = 1:size(circle_cell,1)

    cur_circle = circle_cell{i,1};
    circle_x = [];
    circle_y = [];
    
    for ii = 1:size(cur_circle,1)
        neighborhood = img_skel(floor(cur_circle(ii,2))-5:floor(cur_circle(ii,2))+5, ...
                                floor(cur_circle(ii,1))-5:floor(cur_circle(ii,1))+5);
        if (any(any(neighborhood)))
            circle_x = [circle_x; cur_circle(ii,1)];
            circle_y = [circle_y; cur_circle(ii,2)];
        end
    end

    h = plot(circle_x, circle_y, 'Color', 'red', 'LineWidth', 5);
end


%% Draw Lines
for i = 1:size(line_cell,1)

    cur_line = line_cell{i,1};
    line_x = [];
    line_y = [];

    for ii = 1:size(cur_line,1)
        if (floor(cur_line(ii,2)) < size(img_skel,1)) && (floor(cur_line(ii,1)) < size(img_skel,2) && floor(cur_line(ii,2)) > 0 && floor(cur_line(ii,1)) > 0)
            if (img_skel(floor(cur_line(ii,2)),floor(cur_line(ii,1))) == 1)
                line_x = [line_x; cur_line(ii,1)];
                line_y = [line_y; cur_line(ii,2)];
            end
        end

    end

    h = plot(line_x, line_y, 'Color', 'red', 'LineWidth', 5);
end


