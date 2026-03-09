class Solution {
public:
    int minSubarray(vector<int>& nums, int p) {
        int target_rem = 0;
        for (int num : nums) {
            target_rem = (target_rem + num) % p;
        }
        
        if (target_rem == 0) return 0;

        unordered_map<int, int> mod_map;
        mod_map[0] = -1;
        
        int current_sum = 0;
        int min_len = nums.size();

        for (int i = 0; i < nums.size(); i++) {
            current_sum = (current_sum + nums[i]) % p;
            int needed = (current_sum - target_rem + p) % p;
            
            if (mod_map.find(needed) != mod_map.end()) {
                min_len = min(min_len, i - mod_map[needed]);
            }
            
            mod_map[current_sum] = i;
        }

        return min_len == nums.size() ? -1 : min_len;
    }
};