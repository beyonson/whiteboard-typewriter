function H = hough_circles_acc(BW, radius)
    % Compute Hough accumulator array for finding circles.
    %
    % BW: Binary (black and white) image containing edge pixels
    % radius: Radius of circles to look for, in pixels

    % TODO: Your code here

    % Loop through each edge point of the image, and draw the circle
    H = zeros(size(BW));
    for i = 1:size(BW,1)
        for j = 1:size(BW,2)
            if BW(i,j) == 1

                theta = 0:1:360;
                x_val = round((radius*cosd(theta)) + j);
                y_val = round((radius*sind(theta)) + i);

                for k = 1:length(x_val)
                    if (x_val(k) > 0 && x_val(k) <= size(H, 1) && y_val(k) > 0 && y_val(k) <= size(H,2))
                        H(x_val(k), y_val(k)) = H(x_val(k), y_val(k))+ 1;
                    end
                end

            end
        end
    end

end
