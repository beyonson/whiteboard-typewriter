function peaks = hough_peaks(H, varargin)
    % Find peaks in a Hough accumulator array.
    %
    % Threshold (optional): Threshold at which values of H are considered to be peaks
    % NHoodSize (optional): Size of the suppression neighborhood, [M N]
    %
    % Please see the Matlab documentation for houghpeaks():
    % http://www.mathworks.com/help/images/ref/houghpeaks.html
    % Your code should imitate the matlab implementation.

    %% Parse input arguments
    p = inputParser;
    addOptional(p, 'numpeaks', 1, @isnumeric);
    addParameter(p, 'Threshold', 0.7 * max(H(:)));
    addParameter(p, 'NHoodSize', floor(size(H) / 100.0) * 2 + 1);  % odd values >= size(H)/50
    parse(p, varargin{:});

    numpeaks = p.Results.numpeaks;
    threshold = p.Results.Threshold;
    nHoodSize = p.Results.NHoodSize;

    %% TODO: Your code here

    % Find values greater than threshold
    [peaks_x, peaks_y] = find(H > threshold);

    % Apply neighborhood
    i = 1;
    while i <= length(peaks_x)
        max_peak_x = peaks_x(i) + (nHoodSize(1) - 1)/2;
        min_peak_x = peaks_x(i) - (nHoodSize(1) - 1)/2;
        max_peak_y = peaks_y(i) + (nHoodSize(2) - 1)/2;
        min_peak_y = peaks_y(i) - (nHoodSize(2) - 1)/2;
        
        in_range = peaks_x < max_peak_x & peaks_x > min_peak_x & peaks_y < max_peak_y & peaks_y > min_peak_y;

        if sum(in_range) > 1
            % Find maximum vote and remove others
            idx = 1:length(peaks_x);
            kept_idx = idx(in_range);
            max_val = H(peaks_x(kept_idx(1)), peaks_y(kept_idx(1)));
            max_idx = kept_idx(1);
            for j = 2:length(kept_idx)
                if (max_val < H(peaks_x(kept_idx(j)), peaks_y(kept_idx(j))))
                    max_val = H(peaks_x(kept_idx(j)), peaks_y(kept_idx(j)));
                    max_idx = kept_idx(j);
                end
            end
            in_range(max_idx) = 0;
            peaks_x(in_range) = [];
            peaks_y(in_range) = [];
        end

        i = i + 1;
    end
    
    % Order based on max
    max_vals = [];
    for i = 1:length(peaks_x)
        max_vals = [max_vals; H(peaks_x(i), peaks_y(i))];
    end
    % Get top numpeaks
    [~,idx] = sort(max_vals, 'descend');
    peaks = [peaks_x(idx), peaks_y(idx)];
    if length(peaks) > numpeaks
        peaks = peaks(1:numpeaks, :);
    end
end
