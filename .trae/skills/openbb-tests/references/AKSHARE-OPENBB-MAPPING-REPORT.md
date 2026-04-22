# AKShare to OpenBB Equity Profile Mapping Report

## Overview
This report documents the field mapping between AKShare's stock profile data and OpenBB's EquityInfo model for the `obb.equity.profile` implementation in `openbb_akshare`.

## File References
- **Implementation**: [fetch_equity_info.py](file:///workspace/openbb_akshare/openbb_akshare/utils/fetch_equity_info.py)
- **Data Model**: [equity_profile.py](file:///workspace/openbb_akshare/openbb_akshare/models/equity_profile.py)

## Field Mapping

### Comprehensive Mapping Table

| OpenBB Field | AKShare A-share | AKShare H-share | Description |
|--------------|-------------------|------------------|-------------|
| `symbol` | `symbol` | `symbol` | Stock symbol |
| `name` | `org_name_en` | `comenname` | English company name |
| `ceo` | `chairman` | `chairman` | Company chairman/CEO |
| `company_url` | `org_website` | `web_site` | Company website URL |
| `business_address` | `reg_address_cn` | `rgiofc` | Registered business address |
| `mailing_address` | `office_address_cn` | `hofclctmbu` | Office/mailing address |
| `business_phone_no` | `telephone` | `tel` | Company phone number |
| `hq_address_postal_code` | `postcode` | (empty) | Headquarters postal code |
| `hq_state` | `provincial_name` | (empty) | Headquarters state/province |
| `employees` | `staff_num` | 0 | Number of employees |
| `sector` | `affiliate_industry` | (empty) | Industry sector |
| `industry_category` | `operating_scope` | `refccomty` | Industry category/operating scope |
| `short_description` | `org_cn_introduction` | `comintr` | Short company description |
| `long_description` | `org_cn_introduction` | `comintr` | Long company description |
| `stock_exchange` | `market` (SH/SZ/BJ) | "HKEX" | Stock exchange where traded |
| `org_name_cn` | `org_name_cn` | `comcnname` | Chinese company name |
| `org_short_name_cn` | `org_short_name_cn` | (empty) | Chinese short name |
| `org_short_name_en` | `org_short_name_en` | (empty) | English short name |
| `org_id` | `org_id` | `comunic` | Company ID |
| `established_date` | `established_date` | `incdate` | Date company established |
| `listed_date` | `listed_date` | `lsdateipo` | Date stock listed |
| `actual_issue_vol` | `actual_issue_vol` | `numtissh` | Actual issued volume |
| `reg_asset` | `reg_asset` | 0.0 | Registered assets |
| `issue_price` | `issue_price` | `ispr` | Issue price |
| `currency` | `currency` | "HKD" | Currency type |

## Implementation Details

### Data Retrieval Flow
1. Symbol normalization using `normalize_symbol()`
2. Cache check using `TableCache`
3. AKShare API call:
   - HK stocks: `ak.stock_individual_basic_info_hk_xq()`
   - A-shares: `ak.stock_individual_basic_info_xq()`
4. Data transformation and mapping
5. Cache update
6. Return transformed data

### Key Components

#### EQUITY_INFO_SCHEMA
[fetch_equity_info.py#L12-L40](file:///workspace/openbb_akshare/openbb_akshare/utils/fetch_equity_info.py#L12-L40)

Defines the database schema for cached equity profile data.

#### AKShareEquityProfileData
[equity_profile.py#L28-L304](file:///workspace/openbb_akshare/openbb_akshare/models/equity_profile.py#L28-L304)

Data model that extends OpenBB's EquityInfoData with AKShare-specific fields and validations.

## Notes

### Missing OpenBB Fields
The following OpenBB EquityInfo fields are not populated by the current AKShare implementation:
- `cik` (Central Index Key)
- `cusip` (CUSIP identifier)
- `isin` (International Securities Identification Number)
- `lei` (Legal Entity Identifier)
- `legal_name` (Official legal name)
- `sic` (Standard Industrial Classification)
- `hq_address1` (Address line 1)
- `hq_address2` (Address line 2)
- `hq_address_city` (City)
- `hq_country` (Country)
- `inc_state` (Incorporation state)
- `inc_country` (Incorporation country)
- `entity_legal_form` (Legal form)
- `entity_status` (Entity status)
- `latest_filing_date` (Latest filing date)
- `irs_number` (IRS number)
- `industry_group` (Industry group)
- `template` (Financial template)
- `standardized_active` (Standardized status)
- `first_fundamental_date` (First fundamental date)
- `last_fundamental_date` (Last fundamental date)
- `first_stock_price_date` (First stock price date)
- `last_stock_price_date` (Last stock price date)

### Future Enhancements
1. Map additional fields from AKShare if available
2. Implement better error handling
3. Add more comprehensive data validation
4. Consider alternative data sources for missing fields

## Last Updated
April 22, 2026
