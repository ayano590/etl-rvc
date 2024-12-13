import folder_creator
from api import api_tw_pipe, db_azure_con
import infer_pipeline, freq_spec_pipeline

if __name__ == "__main__":
    folder_creator.main()
    api_tw_pipe.main()
    infer_pipeline.main()
    freq_spec_pipeline.main()
    db_azure_con.main()