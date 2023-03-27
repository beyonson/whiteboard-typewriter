clear
clc
close

%% Import image
img = imread('C:\Users\yasse\Desktop\Senior Design\whiteboard-typewriter\ui\skeletonized\ss2.png');
img = img(:,:,1);

% img = imresize(img, 2);

%% Skeletonization
img = imbinarize((img));
img_skel = img;

BW = img_skel;
[H,T,R] = hough(BW);

P  = houghpeaks(H,10,'threshold',ceil(0.1*max(H(:))));
x = T(P(:,2)); y = R(P(:,1));

lines = houghlines(BW,T,R,P,'FillGap',5,'MinLength',7);
figure, imshow(img_skel), hold on
max_len = 0;
for k = 1:length(lines)
   xy = [lines(k).point1; lines(k).point2];
   plot(xy(:,1),xy(:,2),'LineWidth',2,'Color','green');
   
   img_skel(xy(1,2):xy(2,2),xy(1,1):xy(2,1))=0;

   % Plot beginnings and ends of lines
   plot(xy(1,1),xy(1,2),'x','LineWidth',2,'Color','yellow');
   plot(xy(2,1),xy(2,2),'x','LineWidth',2,'Color','red');

   % Determine the endpoints of the longest line segment
   len = norm(lines(k).point1 - lines(k).point2);
   if ( len > max_len)
      max_len = len;
      xy_long = xy;
   end
end



%% GHT - Circles
[centers, radii, votes] = find_circles(img_skel, [20:1:1000], 0.5, 50);
votes_ratio = votes./radii;

centers = centers(votes > (0.6*max(votes)), :);
radii = radii(votes > (0.6*max(votes)) );
votes = votes(votes > (0.6*max(votes)) );
centers = centers(votes > 50, :);
radii = radii(votes > 50 );
votes = votes(votes > 50 );


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
    circle_cell{i,5} = votes(i);

    h = plot(xunit, yunit, 'Color', 'yellow', 'LineWidth', 5);
end


%% Circles to Arcs
[x,y] = find(img_skel);
arc_cell = cell(size(circle_cell));

for i = 1:size(circle_cell,1)
    cx = circle_cell{i,3};
    cy = circle_cell{i,4};
    r = circle_cell{i,2};

    % Compute distance between circle center and edge points
    dist = sqrt((y-cx).^2 + (x-cy).^2);

    % Determine which edge points are within the circle
    idx = find(dist < r+2 & dist > r-2);
    if isempty(idx)
        continue;
    end

    % Get coordinates of overlapping edge points
    ey = x(idx);
    ex = y(idx);

% %     [idx1, centers1, sumd1] = kmeans([ex,ey], 1);
%     [idx2, centers2, sumd2] = kmeans([ex,ey], 2);
% 
%     if ((sqrt((centers2(1,1)-centers2(2,1)).^2 + (centers2(1,2)-centers2(2,2)).^2))) > r
%         ey = ey(idx2 == mode(idx2));
%         ex = ex(idx2 == mode(idx2));
%     end
    
    % Compute angle of each edge point relative to circle center
    angles = atan2d(-ey+cy, ex-cx);
%     angles(angles < 0) = angles(angles<0) + 360;
    [angles, idx] = sort(angles);
    ey = ey(idx);
    ex = ex(idx);

    angles(1)
    angles(end)

    arc_cell{i,1} = [ex(1), ey(1)];
    arc_cell{i,2} = [ex(end), ey(end)];
    arc_cell{i,3} = [cx, cy];
    arc_cell{i,4} = angles;
    arc_cell{i,5} = abs(angles(1) - angles(end));

end

%% Draw Arcs
for i = 1:size(arc_cell,1)
    radius = norm(arc_cell{i,3} - arc_cell{i,2});
    theta = arc_cell{i,4};
    x = arc_cell{i,3}(1) + radius * cosd(theta);
    y = arc_cell{i,3}(2) - radius * sind(theta);

    % Plot the arc using the plot function
    plot(x, y, 'Color', 'red', 'LineWidth', 5);
end

