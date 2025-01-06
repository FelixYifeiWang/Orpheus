import { Observable } from 'rxjs';
import { PPGReading } from './muse-interfaces';
export interface PPGSample {
    index: number;
    timestamp: number;
    data: number[];
}
export declare function zipSamplesPpg(ppgReadings: Observable<PPGReading>): Observable<PPGSample>;
