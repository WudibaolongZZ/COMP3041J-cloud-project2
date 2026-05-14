from mrjob.job import MRJob
from mrjob.step import MRStep
from mrjob.protocol import RawValueProtocol
import csv
from io import StringIO


class MRLogAnalytics(MRJob):

    OUTPUT_PROTOCOL = RawValueProtocol

    def configure_args(self):
        super(MRLogAnalytics, self).configure_args()

        self.add_passthru_arg(
            '--job',
            type=str,
            help='Choose job: request | error | slow'
        )

    # -----------------------------------
    # Mapper: Request Count
    # -----------------------------------
    def mapper_request(self, _, line):

        if line.startswith("timestamp"):
            return

        try:
            row = next(csv.reader(StringIO(line)))

            service_name = row[3]

            yield service_name, 1

        except:
            pass

    # -----------------------------------
    # Mapper: Error Count
    # -----------------------------------
    def mapper_error(self, _, line):

        if line.startswith("timestamp"):
            return

        try:
            row = next(csv.reader(StringIO(line)))

            service_name = row[3]
            status_code = int(row[6])

            if status_code >= 500:
                yield service_name, 1

        except:
            pass

    # -----------------------------------
    # Mapper: Slow Requests
    # -----------------------------------
    def mapper_slow(self, _, line):

        if line.startswith("timestamp"):
            return

        try:
            row = next(csv.reader(StringIO(line)))

            service_name = row[3]
            endpoint = row[4]
            response_time = int(row[7])

            if response_time > 800:

                key = f"{service_name},{endpoint}"

                yield key, 1

        except:
            pass

    # -----------------------------------
    # Reducer: Sum
    # -----------------------------------
    def reducer_sum(self, key, values):

        total = sum(values)

        yield None, f"{key}\t{total}"

    # -----------------------------------
    # Reducer for Top 10
    # -----------------------------------
    def reducer_slow_sum(self, key, values):

        yield None, (sum(values), key)

    def reducer_top10(self, _, values):

        top10 = sorted(values, reverse=True)[:10]

        for count, key in top10:
            yield None, f"{key}\t{count}"

    # -----------------------------------
    # Steps
    # -----------------------------------
    def steps(self):

        if self.options.job == 'request':

            return [
                MRStep(
                    mapper=self.mapper_request,
                    reducer=self.reducer_sum
                )
            ]

        elif self.options.job == 'error':

            return [
                MRStep(
                    mapper=self.mapper_error,
                    reducer=self.reducer_sum
                )
            ]

        elif self.options.job == 'slow':

            return [
                MRStep(
                    mapper=self.mapper_slow,
                    reducer=self.reducer_slow_sum
                ),
                MRStep(
                    reducer=self.reducer_top10
                )
            ]

        else:
            raise ValueError(
                "Use --job request | error | slow"
            )


if __name__ == '__main__':
    MRLogAnalytics.run()