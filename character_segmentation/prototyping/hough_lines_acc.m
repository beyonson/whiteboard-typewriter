function [H, theta, rho] = hough_lines_acc(BW, varargin)
    %% Parse input arguments
    p = inputParser();
    addParameter(p, 'RhoResolution', 1);
    addParameter(p, 'Theta', linspace(-90, 89, 180));
    parse(p, varargin{:});

    rhoStep = p.Results.RhoResolution;
    theta = p.Results.Theta;



    %% TODO: Your code here

    % Initialize H with zeros
    rho_max = round(sqrt((size(BW,1))^2 + (size(BW,2))^2));
    rho = -rho_max:rhoStep:rho_max;
    H = zeros(length(rho), length(theta));
    
    % Loop through each edge point of the image, and checking different thetas,
    % then voting
    for i = 1:size(BW,1)
        for j = 1:size(BW,2)
            if BW(i,j) == 1
                for k = 1:length(theta)
                    calc_rho = round(j*cosd(theta(k)) + i*sind(theta(k)));
                    H(rho == calc_rho, k) = H(rho == calc_rho, k)+ 1;
                end
            end
        end
    end


end
