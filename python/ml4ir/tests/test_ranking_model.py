from ml4ir.tests.test_base import RankingTestBase
from ml4ir.data.ranking_dataset import RankingDataset
from ml4ir.model.ranking_model import RankingModel
from ml4ir.config import features
import os
import numpy as np


class RankingModelTest(RankingTestBase):
    def run_default_pipeline(self, data_dir: str, data_format: str, feature_config_path: str):
        """Train a model with the default set of args"""
        feature_config = features.parse_config(feature_config_path)

        self.args.metrics = ["categorical_accuracy"]

        ranking_dataset = RankingDataset(
            data_dir=data_dir,
            data_format=data_format,
            features=feature_config,
            max_num_records=self.args.max_num_records,
            loss_key=self.args.loss,
            scoring_key=self.args.scoring,
            batch_size=self.args.batch_size,
            train_pcent_split=self.args.train_pcent_split,
            val_pcent_split=self.args.val_pcent_split,
            test_pcent_split=self.args.test_pcent_split,
            logger=self.logger,
        )
        ranking_model = RankingModel(
            architecture_key=self.args.architecture,
            loss_key=self.args.loss,
            scoring_key=self.args.scoring,
            metrics_keys=self.args.metrics,
            optimizer_key=self.args.optimizer,
            features=feature_config,
            max_num_records=self.args.max_num_records,
            model_file=self.args.model_file,
            learning_rate=self.args.learning_rate,
            learning_rate_decay=self.args.learning_rate_decay,
            compute_intermediate_stats=self.args.compute_intermediate_stats,
            logger=self.logger,
        )

        ranking_model.fit(dataset=ranking_dataset, num_epochs=1, models_dir=self.output_dir)

        loss, accuracy = ranking_model.evaluate(ranking_dataset.test)

        return loss, accuracy

    def test_model_training(self):
        """
        Test model training and evaluate the performance metrics
        """

        # Test model training on CSV data
        data_dir = os.path.join(self.root_data_dir, "csv")
        feature_config_path = os.path.join(self.root_data_dir, "csv", self.feature_config_fname)

        csv_loss, csv_accuracy = self.run_default_pipeline(
            data_dir=data_dir, data_format="csv", feature_config_path=feature_config_path
        )

        # Check if the loss and accuracy on the test set is the same
        assert np.isclose(csv_loss, 1.0754, rtol=0.05)
        assert np.isclose(csv_accuracy, 0.5053, rtol=0.05)

        # Test model training on TFRecord SequenceExample data
        data_dir = os.path.join(self.root_data_dir, "tfrecord")
        feature_config_path = os.path.join(
            self.root_data_dir, "tfrecord", self.feature_config_fname
        )

        tfrecord_loss, tfrecord_accuracy = self.run_default_pipeline(
            data_dir=data_dir, data_format="tfrecord", feature_config_path=feature_config_path
        )

        # Check if the loss and accuracy on the test set is the same
        assert np.isclose(tfrecord_loss, 1.0754, rtol=0.05)
        assert np.isclose(tfrecord_accuracy, 0.5053, rtol=0.05)

        # Compare CSV and TFRecord loss and accuracies
        assert np.isclose(tfrecord_loss, csv_loss, rtol=0.01)
        assert np.isclose(tfrecord_accuracy, csv_accuracy, rtol=0.01)
