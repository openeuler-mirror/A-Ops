#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2022. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN 'AS IS' BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
"""
Time:
Author:
Description: The variational auto-encoder model which will be used to train offline
and online, then predict online.
"""

from cmath import e
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as f
from sklearn.model_selection import train_test_split

from model.base import Predict
from utils.log import Log

log = Log().get_logger()


class VAEPredict(Predict):
    """
    The variational auto-encoder predict model
    """
    def __init__(self, model_path, threshold, *args, **kwargs):
        """
        The variational auto-encoder model initializer.
        :param model_path: The model path
        :param threshold: The threshold of model score
        :param retrain: The retraining tag
        :param args: The args
        :param kwargs: The kwargs
        """
        super().__init__(model_path, threshold, *args, **kwargs)

    def load_model(self):
        """Load variational auto-encoder model"""
        model = torch.load(self.model_path)
        model.eval()
        return model

    def predict(self, x):
        """
        Predicts the anomaly score by variational auto-encoder model
        :param x: The input data
        :return: The predicted labels and corresponding ratio
        """
        if isinstance(x, np.ndarray):
            x = torch.from_numpy(x)

        sample_count = x.shape[0]

        vae = self.load_model()
        output = vae(x)
        y_score = torch.mean(torch.abs(output - x), axis=1).detach().numpy()

        error_thresh = np.quantile(y_score, 0.95)

        y_pred = (y_score > error_thresh) * 1
        if sample_count != 0:
            anomaly_ratio = sum(y_pred) / sample_count
        else:
            anomaly_ratio = 0

        return y_pred, anomaly_ratio

    def is_abnormal(self, x):
        """
        Checks if abnormal points or not
        :param x: The input data
        :return: Existing abnormal points or not
        """
        y_pred, ratio = self.predict(x)
        return ratio >= self.threshold, y_pred, ratio

    def training(self, x):
        """
        Retain the variational auto-encoder model based on the latest raw data
        :return: None
        """
        log.info("Start to execute vae model training...")
        x = x.astype(np.float32)
        x_train, x_test = train_test_split(x, test_size=0.3, random_state=1234, shuffle=True)

        trainer = VAEModelTrain()
        vae = trainer.run(x_train, x_test)
        torch.save(vae, self.model_path)


class VAE(nn.Module):
    """
    The variational auto-encoder model implemented by torch.
    """
    def __init__(self, input_dim, hidden_size, latent_size):
        """
        The variational auto-encoder model initializer.
        :param input_dim: The input dimension
        :param hidden_size: The MN hidden size
        :param latent_size: the NN latent size
        """
        super().__init__()
        self.linear1 = nn.Linear(input_dim, hidden_size)
        self.linear2 = nn.Linear(hidden_size, latent_size)
        self.linear3 = nn.Linear(hidden_size, latent_size)

        self.de_fc1 = nn.Linear(latent_size, hidden_size)
        self.de_fc2 = nn.Linear(hidden_size, input_dim)

        self.kl = 0

    def encoder(self, x):
        """The encoder of variational auto-encoder model"""
        x = torch.relu(self.linear1(x))
        mu = self.linear2(x)
        sigma = f.softplus(self.linear3(x))
        self.kl = 0.5 * torch.sum(torch.exp(sigma) + mu ** 2 - 1. - sigma)
        return mu, sigma

    def decoder(self, z):
        """The decoder of variational auto-encoder model"""
        z = torch.relu(self.de_fc1(z))
        x = self.de_fc2(z)
        return torch.sigmoid(x)

    def forward(self, x):
        """The whole pipeline of variational auto-encoder model"""
        mu, sigma = self.encoder(x)

        std = torch.exp(0.5 * sigma)
        eps = torch.randn_like(std)
        z = eps * std + mu

        out = self.decoder(z)
        return out


class VAEModelTrain:
    """
    The variational auto-encoder model training class
    """
    def __init__(self, batch_size=256, learning_rate=0.001):
        """
        The variational auto-encoder training class initializer
        :param batch_size: The model batch size
        :param learning_rate: The model learning rate
        """
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None

    def run(self, x_train, x_test):
        """
        Run variational auto-encoder model
        :param x_train: The training data
        :param x_test: The test data
        :return: The variational auto-encoder model
        """
        train_data_loader = torch.utils.data.DataLoader(x_train, batch_size=self.batch_size, shuffle=True)
        validate_data_loader = torch.utils.data.DataLoader(x_test, batch_size=self.batch_size, shuffle=True)

        input_dim = x_train.shape[1]
        hidden_size = input_dim // 2
        latent_size = input_dim // 3

        vae = VAE(input_dim, hidden_size, latent_size).to(self.device)
        vae = self.train(vae, train_data_loader, validate_data_loader)
        self.model = vae
        return vae

    def train(self, model, train_data, validate_data, epochs=100):
        """
        Start to train model based on training data and validate data
        :param model: The model
        :param train_data: The training data
        :param validate_data: The validate data
        :param epochs: The epochs of the model
        :return: The model
        """
        log.info(f"Using {self.device} device")

        opt = torch.optim.Adam(model.parameters(), lr=self.learning_rate)
        for epoch in range(epochs):
            train_loss = 0.0
            train_count = 0
            for x in train_data:
                x = x.to(self.device)
                opt.zero_grad()
                x_hat = model(x)
                loss = ((x - x_hat) ** 2).sum() + model.kl
                loss.backward()
                opt.step()
                train_loss += loss.item()
                train_count += x.shape[0]

            model.eval()
            valid_loss = 0.0
            valid_count = 0
            for data in validate_data:
                target = model(data)
                loss = (torch.square(data - target)).sum() + model.kl
                valid_loss += loss.item()
                valid_count += data.shape[0]

            if train_count != 0:
                avg_train_loss =  train_loss / train_count
            else:
                avg_train_loss = 0
                
            if valid_count != 0:
                avg_valid_loss =  valid_loss / valid_count
            else:
                avg_valid_loss = 0

            log.info(f"Epoch(s): {epoch}\ttrain Loss: {avg_train_loss:.2f}\t"
                     f"validate Loss: {avg_valid_loss:.2f}")

        return model
