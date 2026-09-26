class PerformanceValidator:
    def compare(self, train_result, validation_result, test_result) -> dict:
        if not train_result or not test_result:
            return {
                "status": "INVALID_SPLIT",
                "degradation": {},
                "warnings": ["Missing train or test result"]
            }

        train_ret = train_result.total_return
        test_ret = test_result.total_return

        degradation = {
            "train_to_test_return_drop": train_ret - test_ret
        }
        
        warnings = []
        
        if train_ret <= 0:
            warnings.append("Train return is zero or negative. Hard to assess stability.")
            status = "WARNING"
        elif test_ret < train_ret * 0.5:
            status = "SIGNIFICANT_DEGRADATION"
            warnings.append("Test return is less than 50% of Train return.")
        elif test_ret >= train_ret * 0.8:
            status = "STABLE"
        else:
            status = "MODERATE_DEGRADATION"

        return {
            "status": status,
            "degradation": degradation,
            "warnings": warnings
        }
