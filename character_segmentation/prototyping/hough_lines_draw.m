function hough_lines_draw(img, outfile, peaks, rho, theta)

    close all
    fig = imshow(img);
    hold on

    for i = 1:size(peaks)
        cur_theta = theta(peaks(i,2));
        cur_rho = rho(peaks(i,1));

        if cur_theta == 0
            x1 = cur_rho;
            x2 = cur_rho;
            y1 = 1;
            y2 = size(img,1);
        else
            x1 = 1;
            x2 = size(img,2);
            y1 = (-cosd(cur_theta)/sind(cur_theta)) + (cur_rho/sind(cur_theta));
            y2 = (-cosd(cur_theta)/sind(cur_theta))*length(img) + (cur_rho/sind(cur_theta));
        end

        line([x1 x2], [y1 y2], 'Color', 'green', 'LineWidth', 5);

    end
    
    % Save image
    saveas(fig, outfile);

end
