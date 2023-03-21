function [centers, radii, votes] = find_circles(BW, radius_range, thresh, nhood)

    centers = [];
    radii = [];
    votes = [];

    for i = 1:length(radius_range)

        H = hough_circles_acc(BW, radius_range(i));
        %cur_centers = hough_peaks(H, 'numpeaks', 5, 'Threshold', 0.85 * max(H(:)), 'NHoodSize', floor(size(H) / 100.0) * 2 + 1);
        cur_centers = hough_peaks(H, 'numpeaks', 5, 'Threshold', thresh * max(H(:)), 'NHoodSize', [nhood nhood]);
%         cur_centers = hough_peaks(H, 'numpeaks', 50, 'Threshold', 0.90 * max(H(:))'NHoodSize', [50 50]);
        for j = 1:size(cur_centers,1)
            cur_vote = H(cur_centers(j,1), cur_centers(j,2));
            votes = [votes; cur_vote];
        end
        centers = [centers; cur_centers];
        radii = [radii; repmat(radius_range(i), size(cur_centers,1), 1)];

    end



    % Remove centers that are too close based on votes
    i = 1;
    nHoodSize = nhood;
    centers_x = centers(:,1);
    centers_y = centers(:,2);
    while i <= length(votes)
        max_peak_x = centers_x(i) + (nHoodSize - 1)/2;
        min_peak_x = centers_x(i) - (nHoodSize - 1)/2;
        max_peak_y = centers_y(i) + (nHoodSize - 1)/2;
        min_peak_y = centers_y(i) - (nHoodSize - 1)/2;
        
        in_range = centers_x < max_peak_x & centers_x > min_peak_x & centers_y < max_peak_y & centers_y > min_peak_y;
        
        if sum(in_range) > 1
            % Find maximum vote and remove others
            idx = 1:length(centers_x);
            kept_idx = idx(in_range);
            [max_val, max_idx] = max(votes(in_range));
            in_range(kept_idx(max_idx)) = 0;
            votes(in_range) = [];
            centers(in_range) = [];
            radii(in_range) = [];
            centers_x(in_range) = [];
            centers_y(in_range) = [];
        end
        i = i + 1;
    end

    centers = [centers_x, centers_y];

end
