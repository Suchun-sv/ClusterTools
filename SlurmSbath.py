import os

#########################################################################
# 模版
class Template(object):
    def __init__(self):
        self.root = """#!/bin/bash
#SBATCH -n 4
#SBATCH --gres gpu:1
#SBATCH -p dell"""
        self.FileNameList = []
        ##########################################################################
        self.JOB_name = "Tune_0" # 显示在squeue中的名字
        self.log_name = "Tune_0.log" # 输出的log名字
        self.bash_name = "Tune_0.sh" # 输出的脚本的名字
        self.env = "TPAMI"
        self.work_dir = '.'
        self.bash_dir = '.'
        self.exec = "PLEASE CHANGE HERE"
        # self.init_text = "source /home/LAB/anaconda3/bin/activate TPAMI"  # 环境启动脚本
    
    def save(self, save=True, dir='.'):
        dir = self.bash_dir
        self.email_title = self.JOB_name
        self.email_content = os.path.join(self.bash_dir, self.log_name) # 内容必须为文本文件
        root = self.root
        work_dir = 'cd ' + self.work_dir
        inputLog = "#SBATCH -o {}".format(self.log_name)
        sbatch = "#SBATCH -J {}".format(self.JOB_name)
        init_text = "source /home/LAB/anaconda3/bin/activate {}".format(self.env)
        # log_dir = 'cd ' + self.bash_dir
        sendmail = "python sendmail.py -c {} -s {}".format(self.email_content, self.email_title)
        exec = self.exec
        File_name = self.bash_name
        self.__check()

        text = (root + '\n' +
                inputLog + '\n' +
                sbatch + '\n' +
                work_dir + '\n' +
                init_text + '\n' +
                exec + '\n' +
                # log_dir + '\n' +
                sendmail
                )
        if save:
            if not os.path.exists(dir):
                os.makedirs(dir)
            with open(os.path.join(dir, File_name), 'w') as f:
                f.write(text)
                print(os.path.join(dir, File_name), " created!")
            assert File_name not in self.FileNameList, f"the {File_name} had been created!!!"
            self.FileNameList.append(File_name)
            self.save_run_all_dataset(dir)

        return File_name

    def save_run_all_dataset(self, dir='.'):
        with open(os.path.join(dir, "run_all_dataset.sh"), 'w') as f:
            text = ["sbatch " + x + "\n" for x in self.FileNameList]
            f.writelines(text)
    
    def __check(self):
        assert self.log_name.endswith(".log"), "log must end with .log"
        assert self.bash_name.endswith(".sh"), "log must end with .sh"
