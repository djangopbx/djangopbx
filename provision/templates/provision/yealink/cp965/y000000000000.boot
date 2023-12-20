#!version:1.0.0.1
## The header above must appear as-is in the first line

##[$MODEL]include:config <xxx.cfg>
##[$MODEL,$MODEL]include:config "xxx.cfg"  

include:config "y000000000143.cfg"
include:config "{{ prov_defs.mac }}.cfg"

overwrite_mode = {{ prov_defs.yealink_overwrite_mode }}
specific_model.excluded_mode=0
