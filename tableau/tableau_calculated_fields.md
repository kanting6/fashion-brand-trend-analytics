# Tableau Calculated Fields

ATC Rate:
SUM([atc_sessions]) / NULLIF(SUM([traffic_sessions]), 0)

Conversion Rate:
SUM([purchase_sessions]) / NULLIF(SUM([traffic_sessions]), 0)

Return Rate:
SUM([units_returned]) / NULLIF(SUM([units_sold]), 0)

Discount Dependency:
SUM([revenue_discounted]) / NULLIF(SUM([revenue_gross]), 0)
